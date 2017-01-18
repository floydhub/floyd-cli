import os

from floyd.model.access_token import AccessToken


class FloydConfigManager(object):
    """
    Manages ~/.floydconfig file with access token
    """

    def __init__(self):
        self.config_file_path = os.path.expanduser("~/.floydconfig")

    def set_access_token(self, access_token):
        with open(self.config_file_path, "w") as config_file:
            config_file.write(access_token.token)

    def get_access_token(self):
        if not os.path.isfile(self.config_file_path):
            return None

        with open(self.config_file_path, "r") as config_file:
            token = config_file.read()
        return AccessToken(token=token)
