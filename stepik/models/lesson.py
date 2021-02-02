from stepik.client import stepikclient
from stepik.models.entity import Entity
from stepik.models.step import Step
from stepik.utils import entities_loader


class Lesson(Entity):
    def _load(self):
        json = stepikclient.get_lesson(self.user, self.id)

        self._load_from_data(json['lessons'][0])

    def items(self):
        return entities_loader(stepikclient.get_steps, self.user, "steps", self.steps, Step)
