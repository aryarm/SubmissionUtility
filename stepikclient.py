import json
import os

import click
import requests
import time

import attempt_cache
import attempt_cache as attempt_storage
from filemanager import FileManager
from languagemanager import LanguageManager

from settings import STEPIK_API_URL
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


def check_user(user):
    try:
        data = {'grant_type': user.grand_type,
                'client_id': user.client_id,
                'secret_id': user.secret,
                'username': user.username,
                'password': user.password}
        resp = requests.post('https://stepik.org/oauth2/token/', data)

        assert resp.status_code < 300

        user.access_token = (resp.json())['access_token']
        user.refresh_token = (resp.json())['refresh_token']
        user.save()
    except Exception:
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


def get_lesson(user, lesson_id):
    lesson = get_request(STEPIK_API_URL + "/lessons/{}".format(lesson_id), headers=get_headers(user))
    return lesson.json()


def get_submission(user, attempt_id):
    resp = get_request(STEPIK_API_URL + "/submissions/{}".format(attempt_id), headers=get_headers(user))
    return resp.json()


def get_attempt(user, data):
    resp = requests.post(STEPIK_API_URL + "/attempts", data=data, headers=get_headers(user))
    return resp.json()


def get_attempt_id(user, step_id):
    attempt = get_attempt(user, json.dumps({"attempt": {"step": str(step_id)}}))
    try:
        return attempt['attempts'][0]['id']
    except Exception:
        exit_util("Wrong attempt")
    return None


def get_submit(user, url, data):
    resp = post_request(url, data=data, headers=get_headers(user))
    return resp.json()


def get_step(user, step_id):
    step = get_request(STEPIK_API_URL + "/steps/{}".format(step_id), headers=get_headers(user))
    return step.json()


def get_languages_list(user):
    current_step = attempt_storage.get_step_id()
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


def submit_code(user, code, lang=None):
    file_manager = FileManager()

    if not file_manager.is_local_file(code):
        exit_util("FIle {} not found".format(code))
    file_name = code
    code = "".join(open(code).readlines())
    url = STEPIK_API_URL + "/submissions"
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
        language = LanguageManager().programming_language.get(os.path.splitext(file_name)[1])
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
    submit = get_submit(user, url, json.dumps(submission))
    evaluate(user, submit['submissions'][0]['id'])


def set_step(user, step_url):
    click.secho("\nSetting connection to the page..", bold=True)
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
    except Exception:
        exit_util("You do not have permission to perform this action.")
    click.secho("Connecting completed!", fg="green", bold=True)


def get_courses(user, **kwargs):
    courses = get_request(STEPIK_API_URL + "/courses/", params=kwargs, headers=get_headers(user))
    return courses.json()


def get_course(user, course_id):
    courses = get_request(STEPIK_API_URL + "/courses/{}".format(course_id), headers=get_headers(user))
    return courses.json()


def get_sections(user, ids, page):
    url = STEPIK_API_URL + "/sections/?" + prepare_ids(ids) + '&page=' + str(page)
    courses = get_request(url, headers=get_headers(user))
    return courses.json()


def get_units(user, ids, page):
    url = STEPIK_API_URL + "/units/?" + prepare_ids(ids) + '&page=' + str(page)
    units = get_request(url, headers=get_headers(user))
    return units.json()


def get_section(user, section_id):
    courses = get_request(STEPIK_API_URL + "/sections/{}".format(section_id), headers=get_headers(user))
    return courses.json()


def get_lessons(user, ids, page):
    url = STEPIK_API_URL + "/lessons/?" + prepare_ids(ids) + '&page=' + str(page)
    lessons = get_request(url, headers=get_headers(user))
    return lessons.json()


def get_steps(user, ids, page):
    url = STEPIK_API_URL + "/steps/?" + prepare_ids(ids) + '&page=' + str(page)
    lessons = get_request(url, headers=get_headers(user))
    return lessons.json()
