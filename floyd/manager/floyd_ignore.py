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
        if os.path.isfile(cls.CONFIG_FILE_PATH):
            floyd_logger.debug("floyd ignore file already present at {}".format(cls.CONFIG_FILE_PATH))
            return

        floyd_logger.debug("Setting default floyd ignore in the file {}".format(cls.CONFIG_FILE_PATH))

        with open(cls.CONFIG_FILE_PATH, "w") as config_file:
            config_file.write(DEFAULT_FLOYD_IGNORE_LIST)

    @classmethod
    def get_lists(cls, config_file_path=None):
        config_file_path = config_file_path or cls.CONFIG_FILE_PATH

        if not os.path.isfile(config_file_path):
            return ([], [])

        ignore_list = []
        whitelist = []
        with open(config_file_path, "r") as floyd_ignore_file:
            for line in floyd_ignore_file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if line.startswith('!'):
                    whitelist.append(line[1:])
                    continue

                # To allow escaping file names that start with !, #, or \,
                # remove the escaping \
                if line.startswith('\\'):
                    line = line[1:]

                ignore_list.append(line)

        return (ignore_list, whitelist)
