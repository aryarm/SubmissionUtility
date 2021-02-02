import datetime

from .settings import ATTEMPT_FILE
from .client.attempt import Attempt
from .filemanager import FileManager

_file_manager = FileManager()


def clear():
    set_data({})


def get_data():
    try:
        return _file_manager.read_json(ATTEMPT_FILE)
    except FileNotFoundError:
        clear()
        return {}


def set_data(data):
    _file_manager.write_json(ATTEMPT_FILE, data)


def get_step_id(data=None):
    if data is None:
        data = get_data()
    try:
        position = data['current_position']
        return data['steps'][position - 1]
    except KeyError:
        return None


def set_attempt(attempt, data=None):
    if data is None:
        data = get_data()
    if 'attempts' not in data:
        data['attempts'] = {}
    data['attempts'][str(attempt.step_id)] = attempt.json()
    set_data(data)


def get_attempt(step_id, data=None):
    if data is None:
        data = get_data()
    attempt = data['attempts'][str(step_id)]
    return Attempt(
        int(attempt['id']), attempt['start_time'], attempt['due'],
        int(attempt['step_id']), attempt['status']
    )


def set_lesson_id(lesson_id):
    data = get_data()
    data['lesson_id'] = lesson_id
    set_data(data)


def get_lesson_id(data=None):
    if data is None:
        data = get_data()
    try:
        return data['lesson_id']
    except KeyError:
        return None


def get_current_position(data=None):
    if data is None:
        data = get_data()
    try:
        return data['current_position']
    except KeyError:
        return None
