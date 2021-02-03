import re
import sys

import click


def exit_util(message, exit_code=1):
    click.secho(message, fg="red", bold=True, err=True)
    sys.exit(exit_code)


def get_lesson_id(step_url):
    match = re.search(r'lesson/.*?(\d+)/', step_url)
    if match is None:
        return match
    return match.group(1)


def get_step_id(step_url):
    match = re.search(r'step/(\d+)', step_url)
    if match is None:
        return 0
    return int(match.group(1))


def prepare_ids(ids):
    return "&".join(map(lambda id: "ids[]=" + str(id), ids))


def entities_loader(getter, user, key, ids, entity_class):
    has_next = True
    page_index = 1
    entities = list()

    while has_next:
        page = getter(user, ids, page_index)
        has_next = page['meta']['has_next']
        page_index += 1
        page = page[key]
        entities_list = list(map(lambda entity: entity_class(user, entity), page))
        entities.extend(entities_list)

    return entities


def all_entities_loader(getter, user, key, entity_class, **kwargs):
    has_next = True
    page_index = 1
    entities = list()

    while has_next:
        kwargs['page'] = page_index
        page = getter(user, **kwargs)
        has_next = page['meta']['has_next']
        page_index += 1
        page = page[key]
        entities_list = list(map(lambda entity: entity_class(user, entity), page))
        entities.extend(entities_list)

    return entities
