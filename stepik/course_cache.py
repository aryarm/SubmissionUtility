from pathlib import Path

from .filemanager import FileManager
from .models.course import Course
from .settings import COURSE_CACHE_FILE


class CourseCache():
    def __init__(self, course=None, cache_path=COURSE_CACHE_FILE):
        self.file_manager = FileManager()
        self.path = cache_path
        self.course = course
        self._loaded = False
        if not isinstance(cache_path, Path):
            self.path = Path(self.path)
        if course is not None:
            self._initialize_empty_cache()


    def _initialize_empty_cache(self):
        self.data = {'course': [self.course.id, self.course.title], 'lessons': []}


    def load(self, user):
        """try to load the cache for a course. return success status"""
        if not self._loaded:
            try:
                data = self.file_manager.read_json(self.path)
            except FileNotFoundError:
                return False
            if self.course is None:
                # we just create a dummy Course class here, since creating the actual
                # class would require another http request
                self.course = type('Course', (), {})()
                self.course.id = data['current']
                self.course.title = ""
                self._initialize_empty_cache()
            if data['current'] != self.course.id:
                if str(self.course.id) not in data['courses']:
                    return False
                self._save_as_current(data)
            self.data['lessons'] = list(map(int, data['courses'][str(self.course.id)]['lessons']))
            self._loaded = True
        return self._loaded


    def save(self):
        try:
            data = self.file_manager.read_json(self.path)
            data['courses'][str(self.course.id)] = self.data
            data['current'] = self.course.id
        except FileNotFoundError:
            data = {'current': self.course.id, 'courses': {self.course.id: self.data}}
        self.file_manager.write_json(self.path, data)


    def _save_as_current(self, data=None):
        if data is None:
            data = self.file_manager.read_json(self.path)
        data['current'] = self.course.id
        self.file_manager.write_json(self.path, data)


    def update(self):
        """create a cache of all of the lessons in the course"""
        self.data['lessons'] = [
            lesson.id for section in self.course.items()
            for lesson in section.items()
        ]
        self.save()


    def get_next_lesson(self, lesson_id, direction, last_pos=None):
        # if the most recent position is not set, just make it be one of the extremes
        if last_pos is None:
            last_pos = (0, len(self.data['lessons'])-1)[direction < 0]
        # find the current position of this lesson in the list
        # implemented differently depending on the provided direction
        if direction > 0:
            lesson_pos = self.data['lessons'].index(lesson_id, last_pos)
        else:
            last_pos = len(self.data['lessons']) - (last_pos + 1)
            lesson_pos = self.data['lessons'][::-1].index(lesson_id, last_pos)
            lesson_pos = len(self.data['lessons']) - (lesson_pos + 1)
        # get the next lesson and its position
        lesson_pos += direction
        return self.data['lessons'][lesson_pos], lesson_pos

