import os

from floyd.constants import DEFAULT_FLOYD_IGNORE_LIST
from floyd.log import logger as floyd_logger


class FloydIgnoreManager(object):
    """
    Manages .floydignore file in the current directory
    """

    CONFIG_FILE_PATH = os.path.join(os.getcwd() + "/.floydignore")

    @classmethod
    def init(cls):
        floyd_logger.debug("Setting default floyd ignore in the file {}".format(cls.CONFIG_FILE_PATH))

        with open(cls.CONFIG_FILE_PATH, "w") as config_file:
            config_file.write(DEFAULT_FLOYD_IGNORE_LIST)

    @classmethod
    def get_list(cls):
        if not os.path.isfile(cls.CONFIG_FILE_PATH):
            return []

        ignore_dirs = []
        with open(cls.CONFIG_FILE_PATH, "r") as floyd_ignore_file:
            for line in floyd_ignore_file:
                line = line.strip()
                if line and not line.startswith('#'):
                    ignore_dirs.append(line)

        return ignore_dirs
