import json

from floyd.client.base import FloydHttpClient
from floyd.exceptions import FloydException
from floyd.model.access_token import AccessToken


class AuthClient(FloydHttpClient):
    """
    Auth specific client
    """
    def __init__(self):
        self.url = "/user/login/"
        super(AuthClient, self).__init__()

    def login(self, credentials):
        response = self.request("POST",
                                self.url,
                                data=json.dumps(credentials.to_dict()))
        access_token = response.headers.get("access-token")
        expiry = response.headers.get("expiry")

        if not access_token:
            raise FloydException("Access token missing in response", 500)

        return AccessToken(username=credentials.username,
                           token=access_token,
                           expiry=expiry)

    def logout(self):
        self.request("DELETE", url="/user/logout/")
        return True

    def signup(self, signup_request):
        signup_url = "/user/create/"
        response = self.request("POST",
                                signup_url,
                                data=json.dumps(signup_request.to_dict()))
        access_token = response.headers.get("access-token")
        expiry = response.headers.get("expiry")

        if not access_token:
            raise FloydException("Access token missing in response", 500)

        return AccessToken(username=signup_request.username,
                           token=access_token,
                           expiry=expiry)
