import json
import os

from floyd.exceptions import FloydException
from floyd.model.experiment_config import ExperimentConfig
from floyd.log import logger as floyd_logger


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
            raise FloydException("Missing .floydexpt file, run floyd init first")

        with open(cls.CONFIG_FILE_PATH, "r") as config_file:
            experiment_config = json.loads(config_file.read())

        return ExperimentConfig.from_dict(experiment_config)
