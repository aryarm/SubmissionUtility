from filemanager import FileManager
from settings import CLIENT_FILE, CLIENT_ID, CLIENT_SECRET, GRAND_TYPE_PASSWORD


class User:
    file_manager = FileManager()

    def __init__(self):
        try:
            data = self.file_manager.read_json(CLIENT_FILE)
        except FileNotFoundError:
            data = {}

        self.client_id = data.get('client_id', CLIENT_ID)
        self.secret = data.get('client_secret', CLIENT_SECRET)
        self.username = data.get('username', 'Unknown')
        self.grand_type = data.get('grand_type', GRAND_TYPE_PASSWORD)
        self.access_token = data.get('access_token', '')
        self.refresh_token = data.get('refresh_token', '')
        self.step_type = data.get('step_type', 'code')

        self.save()

    def save(self):
        data = dict()
        data['client_id'] = self.client_id
        data['client_secret'] = self.secret
        data['username'] = self.username
        data['grand_type'] = self.grand_type
        data['access_token'] = self.access_token
        data['refresh_token'] = self.refresh_token
        data['step_type'] = self.step_type

        self.file_manager.write_json(CLIENT_FILE, data)
