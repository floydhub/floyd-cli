import os
from pathlib2 import PurePath

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

    # make sure that subdirectories are also excluded
    ignore_list_expanded = ignore_list + ["{}/**".format(item) for item in ignore_list]
    floyd_logger.debug("Ignoring list : {}".format(ignore_list))
    total_file_size = 0

    for root, dirs, files in os.walk(path):
        ignore_dir = False
        normalized_path = normalize_path(path, root)
        for item in ignore_list_expanded:
            if PurePath(normalized_path).match(item):
                ignore_dir = True
                break

        if ignore_dir:
            floyd_logger.debug("Ignoring directory : {}".format(root))
            continue

        for file_name in files:
            ignore_file = False
            normalized_path = normalize_path(path, os.path.join(root, file_name))
            for item in ignore_list_expanded:
                if PurePath(normalized_path).match(item):
                    ignore_file = True
                    break

            if ignore_file:
                floyd_logger.debug("Ignoring file : {}".format(normalized_path))
                continue

            file_relative_path = os.path.join(root, file_name)
            if separator != '/':  # convert relative paths to Unix style
                file_relative_path = file_relative_path.replace(os.path.sep, '/')
            file_full_path = os.path.join(os.getcwd(), root, file_name)

            local_files.append((file_type, (file_relative_path, open(file_full_path, 'rb'), 'text/plain')))
            total_file_size += os.path.getsize(file_full_path)

    return (local_files, sizeof_fmt(total_file_size))


def normalize_path(project_root, path):
    """
    Convert `path` to a UNIX style path, where `project_root` becomes the root
    of an imaginery file system (i.e. becomes just an initial "/").
    """
    if os.path.sep != '/':
        path = path.replace(os.path.sep, '/')
        project_root = project_root.replace(os.path.sep, '/')

    path = path[len(project_root):] if path.startswith(project_root) else path
    path = '/' + path if not path.startswith('/') else path

    return path


def sizeof_fmt(num, suffix='B'):
    """
    Print in human friendly format
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
