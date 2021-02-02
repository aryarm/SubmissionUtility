from stepik.client import stepikclient
from .entity import Entity
from .lesson import Lesson
from .unit import Unit
from ..utils import entities_loader


class Section(Entity):
    def _load(self):
        json = stepikclient.get_section(self.user, self.id)

        self._load_from_data(json['sections'][0])

    def units_set(self):
        return entities_loader(stepikclient.get_units, self.user, "units", self.units, Unit)

    def items(self):
        units = self.units_set()

        ids = list(map(lambda unit: unit.lesson, units))
        return entities_loader(stepikclient.get_lessons, self.user, "lessons", ids, Lesson)