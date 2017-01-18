from floyd.client.base import FloydHttpClient
from floyd.exceptions import FloydException
from floyd.model.access_token import AccessToken


class LoginClient(FloydHttpClient):
    """
    Login specific client
    """
    def __init__(self):
        self.url = "/user/login/"
        super(LoginClient, self).__init__()

    def login(self, credentials):
        response = self.request("POST",
                                self.url,
                                data=credentials.to_dict())
        access_token = response.headers.get("access-token")
        expiry = response.headers.get("expiry")

        if not access_token:
            raise FloydException("Access token missing in response", 500)

        return AccessToken(token=access_token,
                           expiry=expiry)
