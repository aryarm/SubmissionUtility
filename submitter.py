#!/usr/bin/env python
import click
import html2text

import attempt_cache
from client import stepikclient
from client.auth import auth_user_password
from client.consts import STEPIK_HOST
from filemanager import FileManager
from models.course import Course
from models.lesson import Lesson
from models.section import Section
from models.user import User
from navigation import prev_step, next_step
from settings import APP_FOLDER, CLIENT_ID, CLIENT_SECRET, GRAND_TYPE_PASSWORD
from utils import exit_util


@click.group()
@click.version_option()
def main():
    """
    Submitter 0.3
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
    click.echo("Before using, register on https://stepik.org/")

    try:
        user = User()
        user.grand_type = GRAND_TYPE_PASSWORD
        user.client_id = CLIENT_ID
        user.secret = CLIENT_SECRET

        user.username = click.prompt(text="Enter your username")
        password = click.prompt(text="Enter your password", hide_input=True)

        auth_user_password(user, password)

        user.save()

    except Exception as e:
        exit_util("Enter right username and password" + str(e))

    click.secho("Authentication was successfully!", fg="green", bold=True)


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
@click.argument("solution")
@click.option("-l", help="language")
@click.option("--step_id", help="step id")
def submit(solution=None, l=None, step_id=None):
    """
    Submit a solution to stepik system.
    """
    if solution is not None:
        user = User()
        stepikclient.submit_code(user, solution, l, step_id)


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
        current_pos = attempt_cache.get_current_position()
        message = "Switched to the next step successful. Current step is {}".format(current_pos)
        color = "green"
    else:
        message = "Stayed for current step."
        color = "red"

    click.secho(message, bold=True, fg=color)


@main.command()
def prev():
    """
    Switches to the prev code challenge in the lesson
    """
    user = User()
    if prev_step(user, user.step_type):
        current_pos = attempt_cache.get_current_position()
        message = "Switched to the prev step successful. Current step is {}".format(current_pos)
        color = "green"
    else:
        message = "Stayed for current step."
        color = "red"

    click.secho(message, bold=True, fg=color)


@main.command("type")
@click.argument("step_type")
def type_cmd(step_type="code"):
    """
    Filter for step types (default="code")
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
        raise click.BadParameter('Should be a positive integer great than zero.')
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
    click.secho("In order to see the content of the course, use the command: content course <id>")

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
