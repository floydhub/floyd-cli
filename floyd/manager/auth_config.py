import json
import os
import sys

from floyd.model.access_token import AccessToken
from floyd.log import logger as floyd_logger


class AuthConfigManager(object):
    """
    Manages ~/.floydconfig file with access token
    """

    CONFIG_FILE_PATH = os.path.expanduser("~/.floydconfig")

    @classmethod
    def set_access_token(cls, access_token):
        floyd_logger.debug("Setting %s in the file %s", access_token.to_dict(), cls.CONFIG_FILE_PATH)
        with open(cls.CONFIG_FILE_PATH, "w") as config_file:
            config_file.write(json.dumps(access_token.to_dict()))

    @classmethod
    def set_apikey(cls, username, apikey):
        floyd_logger.debug("Setting apikey in the file %s", cls.CONFIG_FILE_PATH)
        with open(cls.CONFIG_FILE_PATH, "w") as config_file:
            config_file.write(json.dumps({'username': username, 'apikey': apikey}))

    @classmethod
    def get_access_token(cls):
        return AccessToken.from_dict(_loads_config(cls.CONFIG_FILE_PATH))

    @classmethod
    def get_auth_header(cls):
        config = _loads_config(cls.CONFIG_FILE_PATH)
        if config.get("apikey"):
            return "apikey " + config.get("apikey")
        elif config.get("token"):
            return "Bearer " + config.get("token")
        return None

    @classmethod
    def purge_access_token(cls):
        if not os.path.isfile(cls.CONFIG_FILE_PATH):
            return True
        os.remove(cls.CONFIG_FILE_PATH)


def _loads_config(file_path):
    if not os.path.isfile(file_path):
        floyd_logger.error(
            'floyd cli config not found, please use "floyd login" command initialize it.')
        sys.exit(5)

    with open(file_path, "r") as config_file:
        access_token_str = config_file.read()

    return json.loads(access_token_str)
