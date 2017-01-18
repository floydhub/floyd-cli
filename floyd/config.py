import os
import json

from floyd.model.access_token import AccessToken
from floyd.model.experiment_config import ExperimentConfig
from floyd.logging import logger as floyd_logger


class AuthConfigManager(object):
    """
    Manages ~/.floydconfig file with access token
    """

    CONFIG_FILE_PATH = os.path.expanduser("~/.floydconfig")

    @classmethod
    def set_access_token(cls, access_token):
        floyd_logger.debug("Setting {} in the file {}".format(access_token.to_dict(),
                                                              cls.CONFIG_FILE_PATH))
        with open(cls.CONFIG_FILE_PATH, "w") as config_file:
            config_file.write(json.dumps(access_token.to_dict()))

    @classmethod
    def get_access_token(cls):
        if not os.path.isfile(cls.CONFIG_FILE_PATH):
            return None

        with open(cls.CONFIG_FILE_PATH, "r") as config_file:
            access_token_str = config_file.read()
        return AccessToken.from_dict(json.loads(access_token_str))

    @classmethod
    def purge_access_token(cls):
        if not os.path.isfile(cls.CONFIG_FILE_PATH):
            return True

        os.remove(cls.CONFIG_FILE_PATH)


class ExperimentConfigManager(object):
    """
    Manages .floydexpt file in the current directory
    """

    CONFIG_FILE_PATH = os.path.join(os.getcwd() + "/.floydexpt")

    @classmethod
    def set_config(cls, experiment_config):
        floyd_logger.debug("Setting {} in the file {}".format(experiment_config.to_dict(),
                                                              cls.CONFIG_FILE_PATH))
        with open(cls.CONFIG_FILE_PATH, "w") as config_file:
            config_file.write(json.dumps(experiment_config.to_dict()))

    @classmethod
    def get_config(cls):
        if not os.path.isfile(cls.CONFIG_FILE_PATH):
            return None

        with open(cls.CONFIG_FILE_PATH, "r") as config_file:
            experiment_config_str = config_file.read()
        return ExperimentConfig.from_dict(json.loads(experiment_config_str))
