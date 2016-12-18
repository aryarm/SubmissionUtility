import stepikclient
from stepik.models.course import Course
from user import User


class Stepik:
    @staticmethod
    def courses_set():
        user = User()
        has_next = True
        page = 1
        courses = list()

        while has_next:
            courses_page = stepikclient.get_courses(user, enrolled='true', page=page)
            has_next = courses_page['meta']['has_next']
            page += 1
            courses.extend(list(map(lambda course: Course(course['id'], course['title']), courses_page['courses'])))

        return courses
