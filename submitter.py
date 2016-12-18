#!/usr/bin/env python
import click
import html2text

import attempt_cache
import stepikclient
from filemanager import FileManager
from navigation import prev_step, next_step
from settings import CLIENT_FILE, APP_FOLDER, CLIENT_ID, CLIENT_SECRET, \
    GRAND_TYPE_PASSWORD, GRAND_TYPE_CREDENTIALS, STEPIK_HOST
from stepik.models.course import Course
from stepik.models.stepik import Stepik
from user import User
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
    lines = 0
    try:
        data = file_manager.read_json(CLIENT_FILE)
        lines += 1
    except Exception:
        pass
    if lines < 1:
        user = User()
        user.clear()
        user.save()
        attempt_cache.clear()


@main.command()
def init():
    """
    Initializes utility: entering client_id and client_secret
    """
    click.echo("Before using, create new Application on https://stepik.org/oauth2/applications/")
    click.secho("Client type - Confidential, Authorization grant type - Client credentials.", fg="red", bold=True)

    try:
        user = User()
        user.grand_type = GRAND_TYPE_CREDENTIALS

        click.secho("Enter your Client id:", bold=True)
        client_id = input()
        click.secho("Enter your Client secret:", bold=True)
        client_secret = input()

        user.client_id = client_id
        user.secret = client_secret

        stepikclient.check_user(user)

        user.save()
    except Exception:
        exit_util("Enter right Client id and Client secret")
    click.secho("Submitter was inited successfully!", fg="green", bold=True)


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
        user.password = click.prompt(text="Enter your password", hide_input=True)

        stepikclient.check_user(user)

        user.save()

    except Exception as e:
        exit_util("Enter right username and password" + str(e))

    click.secho("Authentication was successfully!", fg="green", bold=True)


@main.command()
@click.argument("link")
def step(link=None):
    """
    Setting new step as current target.
    """
    if link is not None:
        user = User()
        stepikclient.set_step(user, link)


@main.command()
@click.argument("solution")
@click.option("-l", help="language")
def submit(solution=None, l=None):
    """
    Submit a solution to stepik system.
    """
    if solution is not None:
        user = User()
        stepikclient.submit_code(user, solution, l)


@main.command()
def lang():
    """
    Displays all available languages for current step
    """
    user = User()

    languages = stepikclient.get_languages_list(user)
    languages.sort()
    click.secho(", ".join(languages), bold=True, nl=False)

    click.echo("")


@main.command()
def next():
    """
    Switches to the next code challenge in the lesson
    """
    message = "Stayed for current step."
    color = "red"
    user = User()
    if next_step(user, user.step_type):
        message = "Switched to the next step successful. Current step is {}".format(
            attempt_cache.get_current_position())
        color = "green"

    click.secho(message, bold=True, fg=color)


@main.command()
def prev():
    """
    Switches to the prev code challenge in the lesson
    """
    message = "Stayed for current step."
    color = "red"
    user = User()
    if prev_step(user, user.step_type):
        message = "Switched to the prev step successful. Current step is {}".format(
            attempt_cache.get_current_position())
        color = "green"

    click.secho(message, bold=True, fg=color)


@main.command()
@click.argument("step_type")
def type(step_type="code"):
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
    step_position = attempt_cache.get_current_position()

    click.secho(STEPIK_HOST + "lesson/{}/step/{}".format(lesson_id, step_position), bold=True, fg="green")


@main.command()
def text():
    """
    Display current step as text
    """
    user = User()

    step_id = attempt_cache.get_step_id()
    step = stepikclient.get_step(user, step_id)

    html = step['steps'][0]['block']['text']
    click.secho(html2text.html2text(html))


@main.command()
def courses():
    """
    Display enrolled courses list
    """
    courses_set = "\n".join(map(str, Stepik.courses_set()))
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
    click.secho("")

