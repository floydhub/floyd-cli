import unittest
from mock import patch, mock_open

from floyd.manager.floyd_ignore import FloydIgnoreManager

class TestFloydIgnoreManagerGetLists(unittest.TestCase):
    """
    Tests FloydIgnoreManager.get_lists()
    """
    @patch('floyd.manager.floyd_ignore.os.path.isfile', return_value=True)
    @patch('floyd.manager.floyd_ignore.open', new_callable=mock_open)
    def test_ignores_commented_lines(self, mopen, _):
        # Manually mock the iterator that imitates the lines read from the file
        file_data = ['', '# comment', '', '*.py']
        mopen.return_value.__iter__.return_value = file_data

        result = FloydIgnoreManager.get_lists()
        self.assertEqual(result, (['*.py'], []))

    @patch('floyd.manager.floyd_ignore.os.path.isfile', return_value=True)
    @patch('floyd.manager.floyd_ignore.open', new_callable=mock_open)
    def test_properly_interprets_whitelisted_globs(self, mopen, _):
        # Manually mock the iterator that imitates the lines read from the file
        file_data = ['', '# comment', '*.py', '!hello.py']
        mopen.return_value.__iter__.return_value = file_data

        result = FloydIgnoreManager.get_lists()
        self.assertEqual(result, (['*.py'], ['hello.py']))

    @patch('floyd.manager.floyd_ignore.os.path.isfile', return_value=False)
    def test_returns_two_empty_lists_if_file_is_not_present(self, _):
        result = FloydIgnoreManager.get_lists()
        self.assertEqual(result, ([], []))

    @patch('floyd.manager.floyd_ignore.os.path.isfile', return_value=True)
    @patch('floyd.manager.floyd_ignore.open', new_callable=mock_open)
    def test_allows_escaping_of_file_names_that_start_with_reserved_chars(self,
                                                                          mopen,
                                                                          _):
        # Manually mock the iterator that imitates the lines read from the file
        file_data = ['', '# comment', '\#file_name', '\!file_name']
        mopen.return_value.__iter__.return_value = file_data

        result = FloydIgnoreManager.get_lists()
        self.assertEqual(result, (['#file_name', '!file_name'], []))
