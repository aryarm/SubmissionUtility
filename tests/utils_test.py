import unittest

from utils import get_lesson_id, get_step_id, prepare_ids

SHORT_LINK = "https://stepik.org/lesson/12752/step/1"
LARGE_LINK = "https://stepik.org/lesson/Что-такое-Java-откуда-она-взялась-и-зачем-нужна-12752/step/1"
WRONG_LINK = "https://stepik.org/"


class Test(unittest.TestCase):
    def test_get_lesson_id_short_link(self):
        lesson_id = get_lesson_id(SHORT_LINK)
        self.assertEqual(lesson_id, "12752")

    def test_get_lesson_id_large_link(self):
        lesson_id = get_lesson_id(LARGE_LINK)
        self.assertEqual(lesson_id, "12752")

    def test_get_lesson_id_wrong_link(self):
        lesson_id = get_lesson_id(WRONG_LINK)
        self.assertEqual(lesson_id, None)

    def test_get_step_id_short_link(self):
        lesson_id = get_step_id(SHORT_LINK)
        self.assertEqual(lesson_id, 1)

    def test_get_step_id_large_link(self):
        lesson_id = get_step_id(LARGE_LINK)
        self.assertEqual(lesson_id, 1)

    def test_get_step_id_wrong_link(self):
        lesson_id = get_step_id(WRONG_LINK)
        self.assertEqual(lesson_id, 0)

    def test_prepare_ids_blank(self):
        ids = []
        params = prepare_ids(ids)
        self.assertEqual(params, '')

    def test_prepare_ids_one(self):
        ids = [123]
        params = prepare_ids(ids)
        self.assertEqual(params, 'ids[]=123')

    def test_prepare_ids_several(self):
        ids = [123, 1, 5, 88]
        params = prepare_ids(ids)
        self.assertEqual(params, 'ids[]=123&ids[]=1&ids[]=5&ids[]=88')

if __name__ == "__main__":
    unittest.main()
