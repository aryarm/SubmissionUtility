#!/usr/bin/env python
import json
import os
import time

import click
import html2text

import attempt_cache
import stepikclient
from filemanager import FileManager
from languagemanager import LanguageManager
from navigation import prev_step, next_step
from settings import CLIENT_FILE, APP_FOLDER, STEPIK_API_URL, CLIENT_ID, CLIENT_SECRET, \
    GRAND_TYPE_PASSWORD, GRAND_TYPE_CREDENTIALS, STEPIK_HOST
from user import User
from utils import exit_util, get_lesson_id, get_step_id


def set_step(user, step_url):
    click.secho("\nSetting connection to the page..", bold=True)
    lesson_id = get_lesson_id(step_url)
    step_id = get_step_id(step_url)

    if lesson_id is None or not step_id:
        exit_util("The link is incorrect.")

    lesson = stepikclient.get_lesson(user, lesson_id)
    attempt_id = stepikclient.get_attempt_id(user, lesson, step_id)
    try:
        attempt_cache.set_attempt_id(attempt_id)
        attempt_cache.set_lesson_id(lesson_id)
    except Exception:
        exit_util("You do not have permission to perform this action.")
    click.secho("Connecting completed!", fg="green", bold=True)


def evaluate(user, attempt_id):
    click.secho("Evaluating", bold=True, fg='white')
    time_out = 0.1
    while True:
        result = stepikclient.get_submission(user, attempt_id)
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
        lesson = stepikclient.get_lesson(user, attempt_cache.get_lesson_id())
        step_pos = attempt_cache.get_current_position()
        attempt_id = stepikclient.get_attempt_id(user, lesson, step_pos)
        attempt_cache.set_attempt_id(attempt_id)
    except Exception:
        pass
    if attempt_id is None:
        exit_util("Please, set the step link!")
    available_languages = stepikclient.get_languages_list(user)
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
    submit = stepikclient.get_submit(user, url, json.dumps(submission))
    evaluate(user, submit['submissions'][0]['id'])


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

        click.secho("Enter your username:", bold=True)
        username = input()
        click.secho("Enter your password:", bold=True)
        password = input()

        user.username = username
        user.password = password

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
        set_step(user, link)


@main.command()
@click.argument("solution")
@click.option("-l", help="language")
def submit(solution=None, l=None):
    """
    Submit a solution to stepik system.
    """
    if solution is not None:
        user = User()
        submit_code(user, solution, l)


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

