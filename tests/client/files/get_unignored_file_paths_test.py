import unittest
from mock import patch

from floyd.client.files import get_unignored_file_paths
from tests.client.mocks import mock_fs1

class TestFilesClientGetUnignoredFilePaths(unittest.TestCase):
    """
    Tests FileClient get_unignored_file_paths()
    """
    @patch('floyd.client.files.os.walk', side_effect=mock_fs1)
    def test_whitelist_overrides_ignore_list(self, pure_path):
        ignore_list = ['*.py', '*.h5', 'baz_dir_3']
        white_list = ['bar_file.py']
        result = get_unignored_file_paths(ignore_list, white_list)
        expected = ['./bar_dir/bar_dir_2/bar_file.py',
                    './baz_dir/baz_dir_2/baz_file.md',
                    './baz_dir/baz_dir_2/baz_file.txt',
                    './README.md']
        result.sort()
        expected.sort()

        self.assertEqual(result, expected)

    @patch('floyd.client.files.os.walk', side_effect=mock_fs1)
    def test_ignoring_a_directory_with_a_trailing_slash(self, pure_path):
        ignore_list = ['*.py', '*.h5', 'baz_dir_2/']
        white_list = []
        result = get_unignored_file_paths(ignore_list, white_list)
        # Does not include the files in baz_dir_2
        expected = ['./README.md']
        result.sort()
        expected.sort()

        self.assertEqual(result, expected)

    @patch('floyd.client.files.os.walk', side_effect=mock_fs1)
    def test_whitelist_does_not_reinclude_files_in_excluded_directories(self, pure_path):
        ignore_list = ['*']
        white_list = ['*.md']
        result = get_unignored_file_paths(ignore_list, white_list)
        # Because other *.md files are within directories that are ignored by
        # the '*' glob, they will not be whitelisted. This follows the expected
        # behavior established by .gitignore logic: "It is not possible to
        # re-include a file if a parent directory of that file is excluded."
        # https://git-scm.com/docs/gitignore#_pattern_format
        expected = ['./README.md']
        result.sort()
        expected.sort()

        self.assertEqual(result, expected)

    @patch('floyd.client.files.os.walk', side_effect=mock_fs1)
    def test_directories_are_ignored(self, pure_path):
        ignore_list = ['foo_dir', 'bar_dir', 'baz_dir']
        white_list = []
        result = get_unignored_file_paths(ignore_list, white_list)
        result.sort()

        # Mocking os.walk() means we are not operating on a real file system.
        # This works fine for most tests, but we have a limitation. Changes to
        # the `root`, `dirs` and `files` variables during an iteration have no
        # impact on subsequent iterations. We leverage the effects of changing
        # the `dirs` variable in place to prevent os.walk() from continuing
        # down a directory that we want to ignore. This behavior is not
        # mockable with our current approach. However, we can see that if a
        # directory is ignored, the files inside that directory are ignored, as
        # we do here with './foo_dir/foo_file.py'
        self.assertFalse('./foo_dir/foo_file.py' in result)
        self.assertTrue('./hello_world.py' in result)
        self.assertTrue('./README.md' in result)
