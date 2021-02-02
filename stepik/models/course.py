from stepik.client import stepikclient
from .entity import Entity
from .section import Section
from .user import User
from ..utils import entities_loader, all_entities_loader


class Course(Entity):
    def _load(self):
        course_json = stepikclient.get_course(self.user, self.id)

        self._load_from_data(course_json['courses'][0])

    @staticmethod
    def all():
        user = User()
        return all_entities_loader(stepikclient.get_courses, user, 'courses', Section, enrolled='true')

    def items(self):
        return entities_loader(stepikclient.get_sections, self.user, "sections", self.sections, Section)

