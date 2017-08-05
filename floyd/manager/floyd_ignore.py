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
            floyd_logger.debug("floyd ignore file already present at %s",
                               cls.CONFIG_FILE_PATH)
            return

        floyd_logger.debug("Setting default floyd ignore in the file %s",
                           cls.CONFIG_FILE_PATH)

        with open(cls.CONFIG_FILE_PATH, "w") as config_file:
            config_file.write(DEFAULT_FLOYD_IGNORE_LIST)

    @classmethod
    def get_lists(cls, config_file_path=None):
        # Remove a preceding '/'. The glob matcher we use will interpret a
        # pattern starging with a '/' as an absolute path, so we remove the
        # '/'. For details on the glob matcher, see:
        # https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.match
        def trim_slash_prefix(path):
            if path.startswith('/'):
                return line[1:]
            return line

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
                    line = line[1:]
                    whitelist.append(trim_slash_prefix(line))
                    continue

                # To allow escaping file names that start with !, #, or \,
                # remove the escaping \
                if line.startswith('\\'):
                    line = line[1:]

                ignore_list.append(trim_slash_prefix(line))

        return (ignore_list, whitelist)
