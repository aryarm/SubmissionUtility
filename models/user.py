from filemanager import FileManager
from settings import CLIENT_FILE, CLIENT_ID, CLIENT_SECRET, GRAND_TYPE_PASSWORD


class User:
    file_manager = FileManager()

    def __init__(self):
        try:
            data = self.file_manager.read_json(CLIENT_FILE)
        except FileNotFoundError:
            data = {}

        User.check(data)

        self.client_id = data['client_id']
        self.secret = data['client_secret']
        self.username = data['username']
        self.grand_type = data['grand_type']
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.step_type = data['step_type']

        self.save()

    @staticmethod
    def check(data):
        if 'client_id' not in data:
            data['client_id'] = CLIENT_ID
        if 'client_secret' not in data:
            data['client_secret'] = CLIENT_SECRET
        if 'grand_type' not in data:
            data['grand_type'] = GRAND_TYPE_PASSWORD
        if 'username' not in data:
            data['username'] = 'Unknown'
        if 'access_token' not in data:
            data['access_token'] = ''
        if 'refresh_token' not in data:
            data['refresh_token'] = ''
        if 'step_type' not in data:
            data['step_type'] = 'code'

    def save(self):
        data = dict()
        data['client_id'] = self.client_id
        data['client_secret'] = self.secret
        data['username'] = self.username
        data['grand_type'] = self.grand_type
        data['access_token'] = self.access_token
        data['refresh_token'] = self.refresh_token
        data['step_type'] = self.step_type

        User.check(data)

        self.file_manager.write_json(CLIENT_FILE, data)

    def clear(self):
        self.client_id = ''
        self.secret = ''
        self.username = ''
        self.grand_type = ''
        self.access_token = ''
        self.refresh_token = ''
        self.step_type = 'code'
