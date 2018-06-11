import requests

import floyd
from floyd.exceptions import AuthenticationException
from floyd.client.base import FloydHttpClient
from floyd.model.user import User


class AuthClient(FloydHttpClient):
    """
    Auth/User specific client
    """
    def __init__(self):
        self.base_url = "{}/api/v1/user/".format(floyd.floyd_host)

    def get_user(self, access_token, is_apikey=False):
        # This is a special case client, because auth_token is not set yet (this is how we verify it)
        # So do not use the shared base client for this!
        auth = ""
        if is_apikey:
            auth = "apikey {}".format(access_token)
        else:
            auth = "Bearer {}".format(access_token)
        response = requests.get(self.base_url, headers={"Authorization": auth})
        try:
            user_dict = response.json()
            response.raise_for_status()
        except Exception:
            if response.status_code == 401:
                raise AuthenticationException("Invalid Token.\nSee http://docs.floydhub.com/faqs/authentication/ for help")  # noqa
            raise AuthenticationException("Login failed.\nSee http://docs.floydhub.com/faqs/authentication/ for help")

        return User.from_dict(user_dict)

    def login(self, credentials):
        # This is another special case client, because auth_token is not set yet (this is how we get the token)
        # So do not use the shared base client for this!
        response = requests.post('%slogin' % self.base_url,
                                 json=credentials.to_dict())
        try:
            token_dict = response.json()
            response.raise_for_status()
        except Exception:
            if response.status_code == 401:
                raise AuthenticationException("Invalid credentials")
            raise AuthenticationException("Login failed. Please try logging in using the token. "
                                          "Run login command without username and password parameters.")

        return token_dict.get('access_token')
