import os
import sys
import tarfile
import signal
import errno

from pathlib2 import PurePath
from shutil import rmtree

# Use the built-in version of scandir if possible, otherwise
# use the scandir module version
try:
    from os import scandir
except ImportError:
    from scandir import scandir  # noqa: F401
from clint.textui.progress import Bar as ProgressBar

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


class DataCompressor(object):
    """
    Local Data Compression with progress bar.
    """
    def __init__(self,
                 source_dir,
                 filename):
        # Data directory to compress
        self.source_dir = source_dir
        # Archive (Tar file) name
        # e.g. "/tmp/contents.tar.gz"
        self.filename = filename

        # Prgress Bar for tracking data compression
        self.__compression_bar = None

        # Number of files to compress
        self.__files_to_compress = 0
        self.__get_nfiles_to_compress()

        # Number of files already compressed
        self.__files_compressed = 0

    def __get_nfiles_to_compress(self):
        """
        Return the number of files to compress

        Note: it should take about 0.1s for counting 100k files on a dual core machine
        """
        floyd_logger.info("Get number of files to compress... (this could take a few seconds)")
        paths = [self.source_dir]
        try:
            # Traverse each subdirs of source_dir and count files/dirs
            while paths:
                path = paths.pop()
                for item in scandir(path):
                    if item.is_dir():
                        paths.append(item.path)
                        self.__files_to_compress += 1
                    elif item.is_file():
                        self.__files_to_compress += 1
        except OSError as e:
            # OSError: [Errno 13] Permission denied
            if e.errno == errno.EACCES:
                self.source_dir = os.getcwd() if self.source_dir == '.' else self.source_dir  # Expand cwd
                sys.exit(("Permission denied. Make sure to have read permission "
                          "for all the files and directories in the path: %s")
                         % (self.source_dir))
        floyd_logger.info("Compressing %d files", self.__files_to_compress)

    def create_tarfile(self):
        """
        Create a tar file with the contents of the current directory
        """
        floyd_logger.info("Compressing data...")
        # Show progress bar (file_compressed/file_to_compress)
        self.__compression_bar = ProgressBar(expected_size=self.__files_to_compress, filled_char='=')

        # Auxiliary functions
        def dfilter_file_counter(tarinfo):
            """
            Dummy filter function used to track the progression at file levels.
            """
            self.__compression_bar.show(self.__files_compressed)
            self.__files_compressed += 1
            return tarinfo

        def warn_purge_exit(info_msg, filename, progress_bar, exit_msg):
            """
            Warn the user that's something went wrong,
            remove the tarball and provide an exit message.
            """
            progress_bar.done()
            floyd_logger.info(info_msg)
            rmtree(os.path.dirname(filename))
            sys.exit(exit_msg)

        try:
            # Define the default signal handler for catching: Ctrl-C
            signal.signal(signal.SIGINT, signal.default_int_handler)
            with tarfile.open(self.filename, "w:gz") as tar:
                tar.add(self.source_dir, arcname=os.path.basename(self.source_dir), filter=dfilter_file_counter)
            self.__compression_bar.done()
        except (OSError, IOError) as e:
            # OSError: [Errno 13] Permission denied
            if e.errno == errno.EACCES:
                self.source_dir = os.getcwd() if self.source_dir == '.' else self.source_dir  # Expand cwd
                warn_purge_exit(info_msg="Permission denied. Removing compressed data...",
                                filename=self.filename,
                                progress_bar=self.__compression_bar,
                                exit_msg=("Permission denied. Make sure to have read permission "
                                          "for all the files and directories in the path: %s")
                                % (self.source_dir))
            # OSError: [Errno 28] No Space Left on Device (IOError on python2.7)
            elif e.errno == errno.ENOSPC:
                dir_path = os.path.dirname(self.filename)
                warn_purge_exit(info_msg="No space left. Removing compressed data...",
                                filename=self.filename,
                                progress_bar=self.__compression_bar,
                                exit_msg=("No space left when compressing your data in: %s.\n"
                                          "Make sure to have enough space before uploading your data.")
                                % (os.path.abspath(dir_path)))

        except KeyboardInterrupt:  # Purge tarball on Ctrl-C
            warn_purge_exit(info_msg="Ctrl-C signal detected: Removing compressed data...",
                            filename=self.filename,
                            progress_bar=self.__compression_bar,
                            exit_msg="Stopped the data upload gracefully.")
