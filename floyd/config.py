import os

from floyd.model.access_token import AccessToken


class FloydConfigManager(object):
    """
    Manages ~/.floydconfig file with access token
    """

    CONFIG_FILE_PATH = os.path.expanduser("~/.floydconfig")

    @classmethod
    def set_access_token(cls, access_token):
        with open(cls.CONFIG_FILE_PATH, "w") as config_file:
            config_file.write(access_token.token)

    @classmethod
    def get_access_token(cls):
        if not os.path.isfile(cls.CONFIG_FILE_PATH):
            return None

        with open(cls.CONFIG_FILE_PATH, "r") as config_file:
            token = config_file.read()
        return AccessToken(token=token)

    @classmethod
    def purge_access_token(cls):
        if not os.path.isfile(cls.CONFIG_FILE_PATH):
            return True

        os.remove(cls.CONFIG_FILE_PATH)
