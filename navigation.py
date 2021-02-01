import attempt_cache
from models.lesson import Lesson
from models.section import Section
from course_cache import CourseCache

FORWARD = 1
BACK = -1

cached_lessons = CourseCache()

def update_step_position(position, steps, direction):
    position += direction
    if position > len(steps) or position < 1:
        # if we get here, it means we've run out of steps in this lesson!
        raise ValueError
    return position

def navigate(user, step_type, direction, course_cache=None):
    data = attempt_cache.get_data()
    try:
        position = data['current_position']
        lesson = Lesson.get(user, data['lesson_id'])
        steps = lesson.items()
    except KeyError:
        return False

    # ensure that direction is either -1 or 1
    # idk why we have to do this, but it was in the original code
    direction = (-1,1)[direction > 0]

    lesson_pos = None
    while True:
        try:
            position = update_step_position(position, steps, direction)
        except ValueError:
            if course_cache is None:
                break
            else:
                try:
                    lesson_id, lesson_pos = course_cache.get_next_lesson(
                        lesson.id, direction, lesson_pos
                    )
                except ValueError:
                    # if there isn't a next lesson
                    raise
                    break
                lesson = Lesson.get(user, lesson_id)
                data['lesson_id'] = lesson.id
                steps = lesson.items()
                data['steps'] = [s.id for s in steps]
                position = (0, len(steps))[direction < 0]
                continue
        step = steps[position-1]
        if step_type == "all" or step.block['name'] == step_type:
            data['current_position'] = position
            attempt_cache.set_data(data)
            return True
    return False


def next_step(user, step_type):
    cached_lessons.load()
    return navigate(user, step_type, FORWARD, cached_lessons)


def prev_step(user, step_type):
    cached_lessons.load()
    return navigate(user, step_type, BACK, cached_lessons)


def create_course_cache(user, course, out_path):
    """create a cache of all of the lessons in a course"""
    cache = CourseCache(course, out_path)
    for section in course.items():
        for lesson in section.items():
            cache.data['lessons'].append(lesson.id)
    cache.save()
