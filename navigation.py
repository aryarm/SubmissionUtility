import json

import attempt_cache
from stepikclient import get_step, get_attempt

FORWARD = 1
BACK = -1


def navigate(user, step_type, direction):
    data = attempt_cache.get_data()
    steps = data['steps']
    position = data['current_position']

    if direction < 0:
        direction = -1
        start = position - 1
        stop = 0
    else:
        direction = 1
        start = position + 1
        stop = len(steps) + 1

    for step_pos in range(start, stop, direction):
        step = None
        if step_type != "all":
            step = get_step(user, steps[step_pos - 1])
        if step_type == "all" or step['steps'][0]['block']['name'] == step_type:
            data['current_position'] = step_pos
            attempt = get_attempt(user, json.dumps({"attempt": {"step": str(steps[step_pos - 1])}}))
            data['attempt_id'] = attempt['attempts'][0]['id']
            attempt_cache.set_data(data)
            return True
    return False


def next_step(user, step_type):
    return navigate(user, step_type, FORWARD)


def prev_step(user, step_type):
    return navigate(user, step_type, BACK)