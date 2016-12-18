import stepikclient


class Course:
    def __init__(self, course_id, title=None):
        self.id = course_id
        self.title = title

    def __str__(self):
        return "{}\t{}".format(self.id, self.title)

    @classmethod
    def get(cls, user, course_id):
        course_json = stepikclient.get_course(user, course_id)
        title = course_json['courses'][0]['title']
        course = Course(course_id, title)
        course.description = course_json['courses'][0]['description']

        return course
