from pathlib import Path
from filemanager import FileManager
from settings import COURSE_CACHE_FILE


class CourseCache():
    def __init__(self, course=None, cache_path=COURSE_CACHE_FILE):
        self.file_manager = FileManager()
        self.path = cache_path
        self._loaded = False
        if not isinstance(cache_path, Path):
            self.path = Path(self.path)
        if course is not None:
            self.data = {'course': [course.id, course.title], 'lessons': []}


    def load(self):
        if not self._loaded:
            self._loaded = True
            self.data = self.file_manager.read_json(self.path)
            self.data['course'][0] = int(self.data['course'][0])
            self.data['lessons'] = list(map(int, self.data['lessons']))


    def save(self):
        self.file_manager.write_json(self.path, self.data)


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

