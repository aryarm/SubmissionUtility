#!/usr/bin/env python
import click
import html2text
from pathlib import Path

from . import attempt_cache
from .course_cache import CourseCache
from .client import stepikclient
from .client.auth import auth_user_password
from .client.consts import STEPIK_HOST, GRAND_TYPE_CREDENTIALS
from .filemanager import FileManager
from .models.course import Course
from .models.lesson import Lesson
from .models.section import Section
from .models.user import User
from .navigation import prev_step, next_step, create_course_cache
from .settings import APP_FOLDER, COURSE_CACHE_FILE, CLIENT_ID, CLIENT_SECRET
from .utils import exit_util


@click.group()
@click.version_option()
def main():
    """
    The (unofficial) Stepik CLI for students\n
    A command line tool for submitting solutions to stepik.org
    """
    file_manager = FileManager()
    try:
        file_manager.create_dir(APP_FOLDER)
    except OSError:
        exit_util("Can't do anything. Insufficient permissions to folders.")


@main.command()
def auth():
    """
    Authenticate using your OAuth2 credentials.
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
        exit_util("\nError! Double-check that your client ID and client secret are correct." + str(e))

    click.secho("Authentication was successfull!", fg="green", bold=True, err=True)


@main.command("step")
@click.argument("link")
def step_cmd(link=None):
    """
    Navigate the current position to the step at the provided URL.
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
    Attempt a dataset challenge. Writes the downloaded dataset to the provided path.
    """
    user = User()
    try:
        attempt = stepikclient.download_dataset(user, dataset_path, step_id, attempt_id)
    except:
        exit_util("Unable to download dataset.")
    click.secho(str(attempt), bold=True, fg='green', err=True)


@main.command()
@click.argument("solution")
@click.option("-l", help="programming language")
@click.option("--step-id", help="step id")
@click.option("--attempt-id", help="attempt id")
def submit(solution=None, l=None, step_id=None, attempt_id=None):
    """
    Submit a solution to stepik. Use the contents of the provided file path.\n
    Specify the programming language via the -l option if your submission is code.\n
    If you are NOT submitting the solution to a dataset challenge, specify "text" to -l
    """
    if solution is not None:
        user = User()
        try:
            stepikclient.submit_code(user, solution, l, step_id, attempt_id)
        except:
            exit_util("Unable to submit solution. There was some sort of error.")


@main.command()
def lang():
    """
    Lists the available programming languages for the current step.\n
    Assumes the current step has a coding challenge.
    """
    user = User()
    current_step_id = attempt_cache.get_step_id()
    languages = stepikclient.get_languages_list(user, current_step_id)
    languages.sort()
    click.secho(", ".join(languages), bold=True, nl=False)


@main.command("next")
def next_cmd():
    """
    Navigate to the next step in a course.\n
    For the best navigation experience, you should set the course using the "course" command before using this command.\n
    Steps will be filtered according to the current step type. You can use the "type" command to change this.
    """
    user = User()
    if next_step(user, user.step_type):
        current_lesson = attempt_cache.get_lesson_id()
        current_pos = attempt_cache.get_current_position()
        message = "Switched to lesson {}, step {}".format(current_lesson, current_pos)
        color = "green"
    else:
        message = "Unable to switch to next step in this lesson."
        message += "\nIf you would like to proceed to the next lesson, check that you've set the course using the 'course' command."
        color = "red"

    click.secho(message, bold=True, fg=color, err=True)


@main.command()
def prev():
    """
    Navigate to the previous step in a course.\n
    For the best navigation experience, you should set the course using the "course" command before using this command.\n
    Steps will be filtered according to the current step type. You can use the "type" command to change this.
    """
    user = User()
    if prev_step(user, user.step_type):
        current_lesson = attempt_cache.get_lesson_id()
        current_pos = attempt_cache.get_current_position()
        message = "Switched to lesson {}, step {}".format(current_lesson, current_pos)
        color = "green"
    else:
        message = "Unable to switch to previous step in this lesson."
        message += "\nIf you would like to proceed to the previous lesson, check that you've set the course using the 'course' command."
        color = "red"

    click.secho(message, bold=True, fg=color, err=True)


@main.command("type")
@click.argument("step_type", type=click.Choice(['all', 'code', 'text', 'dataset'], case_sensitive=False), default='all')
def type_cmd(step_type="dataset"):
    """
    Filter for steps with this step type.\n
    When navigating using the "next" or "prev" commands, any steps that are not of this type will be skipped.
    """
    user = User()
    user.step_type = step_type
    user.save()

    if step_type == 'all':
        click.secho("Steps will not be filtered for their type when navigating.", bold=True, fg="green", err=True)
    else:
        click.secho("Steps that are not of type {} will be ignored when navigating.".format(step_type), bold=True, fg="green", err=True)


@main.command()
def current():
    """
    Display the URL and step ID of the current step.
    """
    data = attempt_cache.get_data()
    lesson_id = attempt_cache.get_lesson_id(data)
    if lesson_id is None:
        exit_util("You should first set the current step using the 'step' command.")

    step_position = attempt_cache.get_current_position(data)
    step_id = attempt_cache.get_step_id(data)

    click.secho(STEPIK_HOST + "lesson/{}/step/{}\t{}".format(lesson_id, step_position, step_id), bold=True, fg="green")


@main.command()
def text():
    """
    Display the contents of the current step.
    """
    user = User()

    step_id = attempt_cache.get_step_id()
    if step_id is None:
        exit_util("You should first set the current step using the 'step' command.")

    step = stepikclient.get_step(user, step_id)

    html = step['steps'][0]['block']['text']
    click.secho(html2text.html2text(html))


@main.command()
def courses():
    """
    Display a list of your enrolled courses and their course IDs.
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
    Switch to the course that has the provided course ID.\n
    Cache the course for navigation purposes and display a description of the course.
    """
    user = User()
    course = Course.get(user, course_id)
    click.secho(str(course), bold=True)

    cache = create_course_cache(course)
    if cache.load(user):
        click.secho("Retrieved course from cache.", fg='green', err=True)
    else:
        click.secho("Caching course lessons...\nSince this is the first time you are navigating this course, this may take a minute.", bold=True, err=True)
        try:
            cache.update()
        except:
            exit_util("Unable to cache course. Do you have permission to view it?")
        if not cache.load(user):
            exit_util("Something went wrong. We were unable to cache this course.")

    click.secho(html2text.html2text(course.description))


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
    View the content of a course, section, or lesson by its ID.\n
    Format:\n
        content course <course_id>\n
        content section <section_id>\n
        content lesson <lesson_id>\n
    """
    if entity not in _ENTITIES:
        return

    user = User()

    entity_class = _ENTITIES[entity]

    entity = entity_class.get(user, entity_id)

    click.secho(str(entity), bold=True)
    items = "\n".join(map(str, entity.items()))
    click.secho(items)
