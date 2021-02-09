import os
import sys
import json
from pathlib import Path


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
        if isinstance(filename, Path):
            return str(filename)
        return filename

    def read_file(self, filename):
        filename = self.get_name(filename)
        with (
            open(filename, "r") if filename and filename != '-' else sys.stdin
        ) as file:
            for line in file:
                yield line

    def write_to_file(self, filename, content):
        filename = self.get_name(filename)
        with (
            open(filename, "w") if filename and filename != '-' else sys.stdout
        ) as file:
            file.writelines(content)

    def write_json(self, filename, data):
        filename = self.get_name(filename)
        with (
            open(filename, "w") if filename and filename != '-' else sys.stdout
        ) as file:
            json.dump(data, file)

    def read_json(self, filename):
        filename = self.get_name(filename)
        return json.loads((
            open(filename) if filename and filename != '-' else sys.stdin
        ).read())

    @staticmethod
    def is_local_file(filename):
        return os.path.isfile(filename)
