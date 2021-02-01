#!/usr/bin/env python
import click
import html2text

from pathlib import Path
import attempt_cache
from course_cache import CourseCache
from client import stepikclient
from client.auth import auth_user_password
from client.consts import STEPIK_HOST, GRAND_TYPE_CREDENTIALS
from filemanager import FileManager
from models.course import Course
from models.lesson import Lesson
from models.section import Section
from models.user import User
from navigation import prev_step, next_step, create_course_cache
from settings import APP_FOLDER, COURSE_CACHE_FILE, CLIENT_ID, CLIENT_SECRET
from utils import exit_util


@click.group()
@click.version_option()
def main():
    """
    Submitter 0.3\n
    Tools for submitting solutions to stepik.org
    """
    file_manager = FileManager()
    try:
        file_manager.create_dir(APP_FOLDER)
    except OSError:
        exit_util("Can't do anything. Not enough rights to edit folders.")


@main.command()
def auth():
    """
    Authentication using username and password
    """
    click.echo("Enter your registration info from https://stepik.org/oauth2/applications/")

    try:
        user = User()
        user.grand_type = GRAND_TYPE_CREDENTIALS

        if not (CLIENT_ID and CLIENT_SECRET):
            user.client_id = click.prompt(text="Enter your client ID")
            user.secret = click.prompt(text="Enter your client secret")
            click.secho("Authenticating...")
        auth_user_password(user)
        user.save()

    except Exception as e:
        exit_util("Error: you should double-check that your client ID and client secret are correct." + str(e))

    click.secho("Authentication was successfull!", fg="green", bold=True)


@main.command("step")
@click.argument("link")
def step_cmd(link=None):
    """
    Setting new step as current target.
    """
    if link is not None:
        user = User()
        stepikclient.set_step(user, link)

@main.command()
@click.argument("dataset-path", type=Path)
@click.option("--step_id", help="step id")
@click.option("--attempt_id", help="attempt id")
def dataset(dataset_path, step_id=None, attempt_id=None):
    """
    Attempt a dataset challenge.
    """
    user = User()
    attempt = stepikclient.download_dataset(user, dataset_path, step_id, attempt_id)
    click.secho(str(attempt), bold=True, fg='green')


@main.command()
@click.argument("solution")
@click.option("-l", help="language")
@click.option("--step-id", help="step id")
@click.option("--attempt-id", help="attempt id")
def submit(solution=None, l=None, step_id=None, attempt_id=None):
    """
    Submit a solution to stepik.\n
    Specify the programming language via the -l option if your submission is code.\n
    If you are NOT submitting the solution to a dataset challenge, specify "text" to -l
    """
    if solution is not None:
        user = User()
        stepikclient.submit_code(user, solution, l, step_id, attempt_id)


@main.command()
def lang():
    """
    Displays all available languages for current step
    """
    user = User()
    current_step_id = attempt_cache.get_step_id()
    languages = stepikclient.get_languages_list(user, current_step_id)
    languages.sort()
    click.secho(", ".join(languages), bold=True, nl=False)

    click.echo("")


@main.command("next")
def next_cmd():
    """
    Switches to the next code challenge in the lesson
    """
    user = User()
    if next_step(user, user.step_type):
        current_lesson = attempt_cache.get_lesson_id()
        current_pos = attempt_cache.get_current_position()
        message = "Switched to lesson {}, step {}".format(current_lesson, current_pos)
        color = "green"
    else:
        message = "Unable to switch to next step in this lesson."
        message += "\nIf you would like to proceed to the next lesson, check that you've created a course cache using the cache command."
        color = "red"

    click.secho(message, bold=True, fg=color)


@main.command()
def prev():
    """
    Switches to the prev code challenge in the lesson
    """
    user = User()
    if prev_step(user, user.step_type):
        current_lesson = attempt_cache.get_lesson_id()
        current_pos = attempt_cache.get_current_position()
        message = "Switched to lesson {}, step {}".format(current_lesson, current_pos)
        color = "green"
    else:
        message = "Unable to switch to previous step in this lesson."
        message += "\nIf you would like to proceed to the previous lesson, check that you've created a course cache using the 'cache' command."
        color = "red"

    click.secho(message, bold=True, fg=color)


@main.command("type")
@click.argument("step_type", type=click.Choice(['all', 'code', 'text', 'dataset'], case_sensitive=False), default='dataset')
def type_cmd(step_type="dataset"):
    """
    Filter for steps of the provided type
    """
    user = User()
    user.step_type = step_type
    user.save()

    click.secho("Steps will filter for {}".format(step_type), bold=True, fg="green")


@main.command()
def current():
    """
    Display the current step link
    """
    lesson_id = attempt_cache.get_lesson_id()
    if lesson_id is None:
        exit_util("Set current step")

    step_position = attempt_cache.get_current_position()

    click.secho(STEPIK_HOST + "lesson/{}/step/{}".format(lesson_id, step_position), bold=True, fg="green")


@main.command()
def text():
    """
    Display current step as text
    """
    user = User()

    step_id = attempt_cache.get_step_id()
    if step_id is None:
        exit_util("Set current step")

    step = stepikclient.get_step(user, step_id)

    html = step['steps'][0]['block']['text']
    click.secho(html2text.html2text(html))


@main.command()
def courses():
    """
    Display enrolled courses list
    """
    courses_set = "\n".join(map(str, Course.all()))
    click.secho(courses_set)


def validate_id(ctx, param, value):
    if value < 1:
        raise click.BadParameter('Should be a positive integer greater than zero.')
    return value


@main.command('course')
@click.argument("course_id", type=click.INT, callback=validate_id)
def course_cmd(course_id):
    """
    About course
    """
    user = User()
    course = Course.get(user, course_id)
    click.secho(str(course), bold=True)
    click.secho(html2text.html2text(course.description))
    click.secho("In order to see the content of a course, use the command: content course <id>")

_ENTITIES = {'course': Course, 'section': Section, 'lesson': Lesson}


def validate_entity(ctx, param, value):
    value = str(value).lower()
    if value not in _ENTITIES:
        raise click.BadParameter('Should be one from "course", "section", "lesson"')
    return value


@main.command('content')
@click.argument("entity", type=click.STRING, callback=validate_entity)
@click.argument("entity_id", type=click.INT, callback=validate_id)
def content_cmd(entity, entity_id):
    """
    Content Course, Section and Lesson

    Format:

        content course <course_id>

        content section <section_id>

        content lesson <lesson_id>

    """
    if entity not in _ENTITIES:
        return

    user = User()

    entity_class = _ENTITIES[entity]

    entity = entity_class.get(user, entity_id)

    click.secho(str(entity), bold=True)
    items = "\n".join(map(str, entity.items()))
    click.secho(items)

@main.command('cache')
@click.option(
    "--cache_path", type=Path, default=COURSE_CACHE_FILE,
    help='path to a JSON file to which to write the cache (defaults to an internal path)'
)
@click.argument("course_id", type=click.INT, callback=validate_id)
def course_cache(course_id, cache_path=COURSE_CACHE_FILE):
    """
    Cache all of the steps in a course.\n
    You can obtain the course ID by running the 'courses' command.
    """
    user = User()
    course = Course.get(user, course_id)

    click.secho(str(course), bold=True)
    click.secho("Caching... This may take a while.", bold=True)

    create_course_cache(user, course, cache_path)

@main.command('set-cache')
@click.argument("cache_path", type=Path)
def set_course_cache(cache_path):
    """
    Replace the internal course cache with a user-provided one
    """
    cache = CourseCache(cache_path=cache_path)
    cache.load()
    try:
        user = User()
        course = Course.get(user, cache['course'])
        click.secho(str(course), bold=True)
    except:
        click.secho("Unable to load course. Check to make sure the authenticated user has permission", bold=True, fg='color')
    cache.cache_path = COURSE_CACHE_FILE
    cache.save()
