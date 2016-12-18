import attempt_cache
from models.lesson import Lesson

FORWARD = 1
BACK = -1


def navigate(user, step_type, direction):
    data = attempt_cache.get_data()
    try:
        steps = data['steps']
        position = data['current_position']
        lesson_id = data['lesson_id']
    except KeyError:
        return False

    if direction < 0:
        direction = -1
        start = position - 1
        stop = 0
    else:
        direction = 1
        start = position + 1
        stop = len(steps) + 1

    if (position + direction) > len(steps) or (position + direction) < 1:
        return False

    if step_type == "all":
        data['current_position'] = position + direction
        attempt_cache.set_data(data)
        return True

    lesson = Lesson.get(user, lesson_id)

    steps = lesson.items()
    for step_pos in range(start, stop, direction):
        step = steps[step_pos - 1]
        if step.block['name'] == step_type:
            data['current_position'] = step_pos
            attempt_cache.set_data(data)
            return True
    return False


def next_step(user, step_type):
    return navigate(user, step_type, FORWARD)


def prev_step(user, step_type):
    return navigate(user, step_type, BACK)
