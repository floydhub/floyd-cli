import requests

import floyd
from floyd.client.base import FloydHttpClient
from floyd.model.user import User


class AuthClient(FloydHttpClient):
    """
    Auth specific client
    """
    def __init__(self):
        self.base_url = "{}/api/v1/user/".format(floyd.floyd_host)

    def get_user(self, access_token):
        response = requests.get(self.base_url,
                                headers={"Authorization": "Bearer {}".format(access_token)})
        user_dict = response.json()
        return User.from_dict(user_dict)
