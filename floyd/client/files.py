import os
import sys
import tarfile
import signal
import errno

from pathlib2 import PurePath
from shutil import rmtree

from floyd.manager.floyd_ignore import FloydIgnoreManager
from floyd.log import logger as floyd_logger


def get_unignored_file_paths(ignore_list=None, whitelist=None):
    """
    Given an ignore_list and a whitelist of glob patterns, returns the list of
    unignored file paths in the current directory and its subdirectories
    """
    unignored_files = []
    if ignore_list is None:
        ignore_list = []
    if whitelist is None:
        whitelist = []

    for root, dirs, files in os.walk("."):
        floyd_logger.debug("Root:%s, Dirs:%s", root, dirs)

        if ignore_path(unix_style_path(root), ignore_list, whitelist):
            # Reset dirs to avoid going further down this directory.
            # Then continue to the next iteration of os.walk, which causes
            # everything in this directory to be ignored.
            #
            # Note that whitelisted files that are within directories that are
            # ignored will not be whitelisted. This follows the expected
            # behavior established by .gitignore logic:
            # "It is not possible to re-include a file if a parent directory of
            # that file is excluded."
            # https://git-scm.com/docs/gitignore#_pattern_format
            dirs[:] = []
            floyd_logger.debug("Ignoring directory : %s", root)
            continue

        for file_name in files:
            file_path = unix_style_path(os.path.join(root, file_name))
            if ignore_path(file_path, ignore_list, whitelist):
                floyd_logger.debug("Ignoring file : %s", file_name)
                continue

            unignored_files.append(os.path.join(root, file_name))

    return unignored_files


def ignore_path(path, ignore_list=None, whitelist=None):
    """
    Returns a boolean indicating if a path should be ignored given an
    ignore_list and a whitelist of glob patterns.
    """
    if ignore_list is None:
        return True

    should_ignore = matches_glob_list(path, ignore_list)
    if whitelist is None:
        return should_ignore

    return should_ignore and not matches_glob_list(path, whitelist)


def matches_glob_list(path, glob_list):
    """
    Given a list of glob patterns, returns a boolean
    indicating if a path matches any glob in the list
    """
    for glob in glob_list:
        try:
            if PurePath(path).match(glob):
                return True
        except TypeError:
            pass
    return False


def get_files_in_current_directory(file_type):
    """
    Gets the list of files in the current directory and subdirectories.
    Respects .floydignore file if present
    """
    local_files = []
    total_file_size = 0

    ignore_list, whitelist = FloydIgnoreManager.get_lists()

    floyd_logger.debug("Ignoring: %s", ignore_list)
    floyd_logger.debug("Whitelisting: %s", whitelist)

    file_paths = get_unignored_file_paths(ignore_list, whitelist)

    for file_path in file_paths:
        local_files.append((file_type, (unix_style_path(file_path), open(file_path, 'rb'), 'text/plain')))
        total_file_size += os.path.getsize(file_path)

    return (local_files, total_file_size)


def unix_style_path(path):
    if os.path.sep != '/':
        return path.replace(os.path.sep, '/')
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


def warn_purge_exit(info_msg, filename, exit_msg):
    """
    Warn the user that's something went wrong,
    remove the tarball and provide an exit message.
    """
    floyd_logger.info(info_msg)
    rmtree(os.path.dirname(filename))
    sys.exit(exit_msg)


def create_tarfile(source_dir, filename="/tmp/contents.tar.gz"):
    """
    Create a tar file with the contents of the current directory
    """
    try:
        # Define the default signal handler for catching: Ctrl-C
        signal.signal(signal.SIGINT, signal.default_int_handler)
        with tarfile.open(filename, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))

    except OSError as e:
        # OSError: [Errno 13] Permission denied
        if e.errno == errno.EACCES:
            source_dir = os.getcwd() if source_dir == '.' else source_dir  # Expand cwd
            warn_purge_exit(info_msg="Permission denied. Removing compressed data...",
                            filename=filename,
                            exit_msg=("Permission denied. Make sure to have read permission "
                                      "for all the files and directories in the path: %s")
                            % (source_dir))

    except KeyboardInterrupt:  # Purge tarball on Ctrl-C
        warn_purge_exit(info_msg="Ctrl-C signal detected: Removing compressed data...",
                        filename=filename,
                        exit_msg="Stopped the data upload gracefully.")
