import os
import json

import time
import click
import requests
import datetime

from .attempt import Attempt
from .auth import get_headers
from .consts import STEPIK_API_URL, LESSONS_PK, SUBMISSIONS_PK, STEPS_PK, COURSES_PK, ATTEMPTS, SUBMISSIONS, \
    SECTIONS, UNITS, SECTIONS_PK, LESSONS, STEPS

from .. import attempt_cache
from ..filemanager import FileManager
from ..languagemanager import LanguageManager
from ..utils import exit_util, get_lesson_id, get_step_id, prepare_ids


def request(request_type, link, **kwargs):
    resp = None
    try:
        resp = requests.__dict__[request_type](link, **kwargs)
    except Exception as e:
        exit_util(e.args[0])
    if resp.status_code >= 400:
        exit_util("Something went wrong. A request returned {}".format(resp.status_code))
    return resp


def post_request(link, **kwargs):
    return request("post", link, **kwargs)


def get_request(link, **kwargs):
    return request("get", link, **kwargs)


def get_entity(user, entity_id, url_template):
    entity = get_request(url_template.format(entity_id), headers=get_headers(user))
    return entity.json()


def get_course(user, course_id):
    return get_entity(user, course_id, COURSES_PK)


def get_section(user, section_id):
    return get_entity(user, section_id, SECTIONS_PK)


def get_lesson(user, lesson_id):
    return get_entity(user, lesson_id, LESSONS_PK)


def get_submission(user, submission_id):
    return get_entity(user, submission_id, SUBMISSIONS_PK)


def get_step(user, step_id):
    return get_entity(user, step_id, STEPS_PK)


def get_attempt_id(user, step_id):
    data = json.dumps({"attempt": {"step": str(step_id)}})
    attempt = post_request(ATTEMPTS, data=data, headers=get_headers(user))
    return attempt.json()['attempts'][0]['id']


def post_submit(user, data, attempt_id):
    submission_url = SUBMISSIONS[:-1] if SUBMISSIONS.endswith('/') else SUBMISSIONS
    resp = post_request(
        submission_url+"?attempt={}".format(attempt_id),
        data=data, headers=get_headers(user)
    )
    return resp.json()


def get_languages_list(user, step_id):
    if step_id is None:
        exit_util('Please set the current step using the "step" command.')
    step = get_step(user, step_id)
    block = step['steps'][0]['block']
    if block['name'] != 'code':
        exit_util('The current step does not have a coding challenge.')
    languages = block['options']['code_templates']
    return [lang for lang in languages]


def evaluate(user, attempt_id):
    click.secho("Evaluating...", bold=True, fg='white', err=True)
    time_out = 0.1
    while True:
        result = get_submission(user, attempt_id)
        status = result['submissions'][0]['status']
        hint = result['submissions'][0]['hint']
        if status != 'evaluation':
            break
        click.echo("..", nl=False, err=True)
        time.sleep(time_out)
        time_out += time_out
    click.secho("Your solution is {}".format(status), fg=['red', 'green'][status == 'correct'], bold=True)
    if status != 'correct':
        exit_util(hint, 2)


def get_dataset_attempt(user, step_id, attempt_id=None):
    if attempt_id is None:
        data = json.dumps({"attempt": {"step": str(step_id)}})
        try:
            attempt = post_request(ATTEMPTS, data=data, headers=get_headers(user))
            attempt = attempt.json()['attempts'][0]
        except Exception:
            exit_util(
                "Unable to attempt this challenge. Is the current position set to a valid step?\n" + \
                str(attempt)
            )
        if 'dataset_url' not in attempt or not attempt['dataset_url']:
            exit_util("Unable to retrieve dataset from current step. Check that a dataset exists for this step.")
    else:
        try:
            attempt = post_request(ATTEMPTS+"/{}".format(attempt_id), headers=get_headers(user))
            attempt = attempt.json()['attempts'][0]
        except Exception:
            exit_util(
                "Unable to attempt this challenge. Is the current position set to a valid step?\n" + \
                str(attempt)
            )
        if 'dataset_url' not in attempt or not attempt['dataset_url']:
            exit_util("Unable to retrieve dataset from this attempt. Check that a dataset exists for this attempt.")
    return attempt


def download_dataset(user, filename, step_id=None, attempt_id=None):
    data = attempt_cache.get_data()
    if step_id is None:
        step_id = attempt_cache.get_step_id(data)
    attempt = get_dataset_attempt(user, step_id, attempt_id)
    if attempt['dataset_url'].startswith('/api'):
        attempt['dataset_url'] = attempt['dataset_url'][len('/api'):]
    try:
        dataset = get_request(
            STEPIK_API_URL+attempt['dataset_url'],
            headers=get_headers(user)
        )
    except Exception:
        exit_util("Unable to retrieve dataset for attempt {}".format(attempt['id']))
    FileManager().write_to_file(filename, dataset.text)
    start_time = datetime.datetime.now()
    time_left = datetime.timedelta(seconds=int(attempt['time_left']))
    attempt = Attempt(
        attempt['id'], start_time, start_time + time_left,
        attempt['step'], attempt['status']
    )
    attempt_cache.set_attempt(attempt, data)
    return attempt


def submit_code(user, filename, lang=None, step_id=None, attempt_id=None):
    file_manager = FileManager()

    try:
        text_contents = "".join(open(filename).readlines())
    except FileNotFoundError:
        exit_util("File {} not found".format(filename))

    if step_id is None:
        step_id = attempt_cache.get_step_id()
    submission = {
        "submission":
            {
                "reply":{},
                "attempt": attempt_id
            }
    }
    if lang is None:
        try:
            attempt = attempt_cache.get_attempt(step_id)
            if attempt.due < datetime.datetime.now():
                exit_util("This challenge has already expired. Create a new one with the 'dataset' command.")
        except KeyError:
            exit_util("Tried to submit to a dataset challenge, but couldn't find a prior attempt. Please specify the attempt ID via the --attempt-id parameter")
        submission['submission']['reply'] = {
            "file": text_contents
        }
        if submission['submission']['attempt'] is None:
            submission['submission']['attempt'] = attempt.id
    else:
        if attempt_id is None:
            try:
                attempt_id = get_attempt_id(user, step_id)
            except Exception:
                exit_util("Please, set the step link!")
            submission['submission']['attempt'] = attempt_id
        if lang == 'text':
            submission['submission']['reply'] = {
                "text": text_contents,
                "files": []
            }
        else:
            available_languages = get_languages_list(user, step_id)
            if lang in available_languages:
                language = lang
            else:
                language = LanguageManager().programming_language.get(os.path.splitext(filename)[1])
            if language is None:
                exit_util("Doesn't correct extension for programme.")
            if language not in available_languages:
                exit_util("This language not available for current step.")
            submission['submission']['time'] = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
            submission['submission']['reply'] = {
                "code": text_contents,
                "language": language
            }
    submit = post_submit(
        user, json.dumps(submission), submission['submission']['attempt']
    )
    try:
        submission = submit['submissions'][-1]['id']
    except IndexError:
        exit_util("There was a problem with the format of the submission.")
    evaluate(user, submission)


def set_step(user, step_url):
    lesson_id = get_lesson_id(step_url)
    step_id = get_step_id(step_url)

    if lesson_id is None or not step_id:
        exit_util("The link is incorrect.")

    lesson = get_lesson(user, lesson_id)

    steps = None
    try:
        steps = lesson['lessons'][0]['steps']
    except Exception:
        exit_util("Didn't receive such lesson.")
    if len(steps) < step_id or step_id < 1:
        exit_util("Too few steps in the lesson.")

    data = attempt_cache.get_data()
    data['steps'] = steps
    data['current_position'] = step_id
    attempt_cache.set_data(data)
    try:
        attempt_cache.set_lesson_id(lesson_id)
    except PermissionError:
        exit_util("You do not have permission to perform this action.")
    click.secho("Current position set to lesson {}, step {}".format(lesson_id, step_id), fg="green", bold=True)


def get_courses(user, **kwargs):
    courses = get_request(STEPIK_API_URL + "/courses/", params=kwargs, headers=get_headers(user))
    return courses.json()


def get_entities_with_ids(user, ids, page, url):
    url = url + "?" + prepare_ids(ids) + '&page=' + str(page)
    entities = get_request(url, headers=get_headers(user))
    return entities.json()


def get_sections(user, ids, page):
    return get_entities_with_ids(user, ids, page, SECTIONS)


def get_units(user, ids, page):
    return get_entities_with_ids(user, ids, page, UNITS)


def get_lessons(user, ids, page):
    return get_entities_with_ids(user, ids, page, LESSONS)


def get_steps(user, ids, page):
    return get_entities_with_ids(user, ids, page, STEPS)
