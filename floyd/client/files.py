import os

from floyd.manager.floyd_ignore import FloydIgnoreManager
from floyd.log import logger as floyd_logger


def get_files_in_directory(path, file_type):
    """
    Gets the list of files in the directory and subdirectories
    Respects .floydignore file if present
    """
    local_files = []
    separator = os.path.sep
    ignore_list = FloydIgnoreManager.get_list()
    ignore_list_localized = [".{}{}".format(separator, item) for item in ignore_list]
    floyd_logger.debug("Ignoring list : {}".format(ignore_list_localized))
    total_file_size = 0

    for root, dirs, files in os.walk(path):
        ignore_dir = False
        for item in ignore_list_localized:
            if root.startswith(item):
                ignore_dir = True

        if ignore_dir:
            floyd_logger.debug("Ignoring directory : {}".format(root))
            continue

        for file_name in files:
            file_relative_path = os.path.join(root, file_name)
            if separator != '/':  # convert relative paths to Unix style
                file_relative_path = file_relative_path.replace(os.path.sep, '/')
            file_full_path = os.path.join(os.getcwd(), root, file_name)

            local_files.append((file_type, (file_relative_path, open(file_full_path, 'rb'), 'text/plain')))
            total_file_size += os.path.getsize(file_full_path)

    return (local_files, sizeof_fmt(total_file_size))


def sizeof_fmt(num, suffix='B'):
    """
    Print in human friendly format
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
