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
    def get_access_token(cls):
        if not os.path.isfile(cls.CONFIG_FILE_PATH):
            floyd_logger.error(
                'floyd cli config not found, please use "floyd login" command initialize it.')
            sys.exit(5)

        with open(cls.CONFIG_FILE_PATH, "r") as config_file:
            access_token_str = config_file.read()

        return AccessToken.from_dict(json.loads(access_token_str))

    @classmethod
    def purge_access_token(cls):
        if not os.path.isfile(cls.CONFIG_FILE_PATH):
            return True

        os.remove(cls.CONFIG_FILE_PATH)
