from filemanager import FileManager
from settings import ATTEMPT_FILE

_file_manager = FileManager()


def clear():
    _file_manager.write_json(ATTEMPT_FILE, {})


def get_step_id():
    file = _file_manager.read_json(ATTEMPT_FILE)
    position = file['current_position']
    return file['steps'][position - 1]


def set_lesson_id(lesson_id):
    data = _file_manager.read_json(ATTEMPT_FILE)
    data['lesson_id'] = lesson_id
    _file_manager.write_json(ATTEMPT_FILE, data)


def get_lesson_id():
    file = _file_manager.read_json(ATTEMPT_FILE)
    return file['lesson_id']


def get_current_position():
    file = _file_manager.read_json(ATTEMPT_FILE)
    return file['current_position']


def get_data():
    return _file_manager.read_json(ATTEMPT_FILE)


def set_data(data):
    _file_manager.write_json(ATTEMPT_FILE, data)
