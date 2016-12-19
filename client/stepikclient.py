import json
import os

import click
import requests
import time

import attempt_cache
import attempt_cache as attempt_storage
from client.consts import STEPIK_API_URL, LESSONS_PK, SUBMISSIONS_PK, STEPS_PK, COURSES_PK, ATTEMPTS, SUBMISSIONS, \
    SECTIONS, UNITS, SECTIONS_PK, LESSONS, STEPS
from filemanager import FileManager
from languagemanager import LanguageManager

from utils import exit_util, get_lesson_id, get_step_id, prepare_ids


def request(request_type, link, **kwargs):
    resp = None
    try:
        resp = requests.__dict__[request_type](link, **kwargs)
    except Exception as e:
        exit_util(e.args[0])
    if resp.status_code >= 400:
        exit_util("Something went wrong.")
    return resp


def post_request(link, **kwargs):
    return request("post", link, **kwargs)


def get_request(link, **kwargs):
    return request("get", link, **kwargs)


def check_user(user, password):
    try:
        data = {'grant_type': user.grand_type,
                'client_id': user.client_id,
                'secret_id': user.secret,
                'username': user.username,
                'password': password}
        resp = requests.post('https://stepik.org/oauth2/token/', data)

        assert resp.status_code < 300

        user.access_token = (resp.json())['access_token']
        user.refresh_token = (resp.json())['refresh_token']
        user.save()
    except AssertionError:
        exit_util("Check your authentication.")


def get_headers(user):
    return {'Authorization': 'Bearer ' + user.access_token, "content-type": "application/json"}


def refresh_client(user):
    try:
        data = {'grant_type': 'refresh_token',
                'client_id': user.client_id,
                'secret_id': user.secret,
                'refresh_token': user.refresh_token}

        resp = requests.post('https://stepik.org/oauth2/token/', data)

        assert resp.status_code < 300

        user.access_token = (resp.json())['access_token']
        user.refresh_token = (resp.json())['refresh_token']
        user.save()
    except Exception:
        return False

    return True


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
    try:
        attempt = requests.post(ATTEMPTS, data=data, headers=get_headers(user))

        assert attempt.status_code < 300

        return attempt.json()['attempts'][0]['id']
    except KeyError or AssertionError:
        exit_util("Wrong attempt")


def post_submit(user, data):
    resp = post_request(SUBMISSIONS, data=data, headers=get_headers(user))
    return resp.json()


def get_languages_list(user):
    current_step = attempt_storage.get_step_id()
    if current_step == 0:
        exit_util('Set current step.')
    step = get_step(user, current_step)
    block = step['steps'][0]['block']
    if block['name'] != 'code':
        exit_util('Type step is not code.')
    languages = block['options']['code_templates']
    return [lang for lang in languages]


def evaluate(user, attempt_id):
    click.secho("Evaluating", bold=True, fg='white')
    time_out = 0.1
    while True:
        result = get_submission(user, attempt_id)
        status = result['submissions'][0]['status']
        hint = result['submissions'][0]['hint']
        if status != 'evaluation':
            break
        click.echo("..", nl=False)
        time.sleep(time_out)
        time_out += time_out
    click.echo("")
    click.secho("You solution is {}\n{}".format(status, hint), fg=['red', 'green'][status == 'correct'], bold=True)


def submit_code(user, filename, lang=None):
    file_manager = FileManager()

    if not file_manager.is_local_file(filename):
        exit_util("File {} not found".format(filename))
    code = "".join(open(filename).readlines())

    current_time = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())

    attempt_id = None
    try:
        step_id = attempt_cache.get_step_id()
        attempt_id = get_attempt_id(user, step_id)
    except Exception:
        pass
    if attempt_id is None:
        exit_util("Please, set the step link!")
    available_languages = get_languages_list(user)
    if lang in available_languages:
        language = lang
    else:
        language = LanguageManager().programming_language.get(os.path.splitext(filename)[1])
    if language is None:
        exit_util("Doesn't correct extension for programme.")
    if language not in available_languages:
        exit_util("This language not available for current step.")
    submission = {
        "submission":
            {
                "time": current_time,
                "reply":
                    {
                        "code": code,
                        "language": language
                    },
                "attempt": attempt_id
            }
    }

    submit = post_submit(user, json.dumps(submission))
    evaluate(user, submit['submissions'][0]['id'])


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

    data = attempt_storage.get_data()
    data['steps'] = steps
    data['current_position'] = step_id
    attempt_storage.set_data(data)
    try:
        attempt_cache.set_lesson_id(lesson_id)
    except PermissionError:
        exit_util("You do not have permission to perform this action.")
    click.secho("Setting current step completed!", fg="green", bold=True)


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
