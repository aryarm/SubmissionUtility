import requests
import datetime

from ..utils import exit_util


def auth_user_password(user, password=None):
    try:
        expiration = datetime.datetime.now()
        if password:
            data = {'grant_type': user.grand_type,
                    'client_id': user.client_id,
                    'secret_id': user.secret,
                    'username': user.username,
                    'password': password}
            resp = requests.post('https://stepik.org/oauth2/token/', data)
        else:
            auth = requests.auth.HTTPBasicAuth(user.client_id, user.secret)
            data = {'grant_type': user.grand_type}
            resp = requests.post('https://stepik.org/oauth2/token/', data, auth=auth)

        assert resp.status_code < 300

        resp = resp.json()
        user.access_token = resp['access_token']
        user.expiration = expiration + datetime.timedelta(seconds=int(resp['expires_in']))
        user.refresh_token = None
        if 'refresh_token' in resp:
            user.refresh_token = resp['refresh_token']
        user.save()
    except AssertionError:
        exit_util("Check your authentication.")


def get_headers(user):
    return {'Authorization': 'Bearer ' + user.access_token, "content-type": "application/json"}


def refresh_client(user):
    try:
        data = {'grant_type': 'refresh_token',
                'client_id': user.client_id,
                'secret_id': user.secret,
                'refresh_token': user.refresh_token}

        resp = requests.post('https://stepik.org/oauth2/token/', data)

        assert resp.status_code < 300

        user.access_token = (resp.json())['access_token']
        user.refresh_token = (resp.json())['refresh_token']
        user.save()
    except AssertionError:
        return False

    return True
