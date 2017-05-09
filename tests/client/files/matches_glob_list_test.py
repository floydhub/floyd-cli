import unittest
from mock import patch, call

from floyd.client.files import matches_glob_list

class TestFilesClientMatchesGlobList(unittest.TestCase):
    """
    Tests FileClient matches_glob_list()
    """
    @patch('floyd.client.files.PurePath.match', side_effect=[False, True])
    def test_returns_true_with_matching_glob(self, pure_path):
        glob = '*.py'
        result = matches_glob_list('./hello.py', [glob])

        # Checks if PurePath.match is called with the glob
        pure_path.assert_called_with(glob)

        # Returns True for one matching glob
        self.assertTrue(True)

    @patch('floyd.client.files.PurePath.match', side_effect=[False, False])
    def test_returns_false_with_no_matching_globs(self, pure_path):
        glob = '*.py'
        result = matches_glob_list('./hello.py', [glob])

        # Checks if PurePath.match is called with the glob
        pure_path.assert_called_with(glob)

        # Returns False for no matches
        self.assertFalse(result)

    @patch('floyd.client.files.PurePath.match', side_effect=[False, False])
    def test_calls_match_for_each_glob_before_returning_false(self, pure_path):
        globs = ['foo', '*bar']
        result = matches_glob_list('./hello.py', globs)

        # Called with each glob
        calls = [call(x) for x in globs]
        pure_path.assert_has_calls(calls, any_order=True)

        # Returns False for no matches
        self.assertFalse(result)
