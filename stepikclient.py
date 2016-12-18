import json

import requests
import attempt_cache as attempt_storage

from settings import STEPIK_API_URL
from utils import exit_util


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
        exit_util("Check your Client id and Client secret.")


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


# def auth_user(user):
#     if not refresh_client(user):
#         check_user(user)


def get_lesson(user, lesson_id):
    # auth_user(user)

    lesson = get_request(STEPIK_API_URL + "/lessons/{}".format(lesson_id), headers=get_headers(user))
    return lesson.json()


def get_submission(user, attempt_id):
    # auth_user(user)

    resp = get_request(STEPIK_API_URL + "/submissions/{}".format(attempt_id), headers=get_headers(user))
    return resp.json()


def get_attempt(user, data):
    # auth_user(user)

    resp = requests.post(STEPIK_API_URL + "/attempts", data=data, headers=get_headers(user))
    return resp.json()


def get_attempt_id(user, lesson, step_id):
    # auth_user(user)

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
    step_id = steps[step_id - 1]
    attempt_storage.set_data(data)

    attempt = get_attempt(user, json.dumps({"attempt": {"step": str(step_id)}}))
    try:
        return attempt['attempts'][0]['id']
    except Exception:
        exit_util("Wrong attempt")
    return None


def get_submit(user, url, data):
    # auth_user(user)

    resp = post_request(url, data=data, headers=get_headers(user))
    return resp.json()


def get_step(user, step_id):
    step = get_request(STEPIK_API_URL + "/steps/{}".format(step_id), headers=get_headers(user))
    return step.json()


def get_languages_list(user):
    # auth_user(user)
    current_step = attempt_storage.get_step_id()
    step = get_step(user, current_step)
    block = step['steps'][0]['block']
    if block['name'] != 'code':
        exit_util('Type step is not code.')
    languages = block['options']['code_templates']
    return [lang for lang in languages]
