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

    def get_user(self, access_token):
        try:
            response = self.requests.get(self.base_url,
                                         headers={"Authorization": "Bearer {}".format(access_token)})
            user_dict = response.json()
        except Exception:
            raise AuthenticationException("Invalid Token.\nSee http://docs.floydhub.com/faqs/authentication/ for help")

        return User.from_dict(user_dict)
