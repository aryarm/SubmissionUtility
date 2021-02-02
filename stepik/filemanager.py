import os
import json


class FileManager:
    """
    Local file manager
    """

    def __init__(self):
        self.home = os.getcwd()

    def create_dir(self, dir_name):
        dir_name = self.get_name(dir_name)
        try:
            os.mkdir(dir_name)
        except FileExistsError as e:
            return

    def get_name(self, filename):
        return filename

    def read_file(self, filename):
        filename = self.get_name(filename)
        with open(filename, "r") as file:
            for line in file:
                yield line

    def write_to_file(self, filename, content):
        filename = self.get_name(filename)
        with open(filename, "w") as file:
            file.writelines(content)

    def write_json(self, filename, data):
        filename = self.get_name(filename)
        with open(filename, "w") as file:
            json.dump(data, file)

    def read_json(self, filename):
        filename = self.get_name(filename)
        return json.loads(open(filename).read())

    @staticmethod
    def is_local_file(filename):
        return os.path.isfile(filename)
