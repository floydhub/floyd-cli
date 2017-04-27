from click.testing import CliRunner
import unittest
from mock import patch, call

from floyd.cli.data import delete


class TestDataDelete(unittest.TestCase):
    """
    Tests CLI's data delete functionality `floyd data delete`
    """
    def setUp(self):
        self.runner = CliRunner()

    @patch('floyd.cli.data.DataClient')
    def test_with_no_arguments(self, data_client):
        result = self.runner.invoke(delete)

        # No calls to api, exit 0
        data_client.assert_not_called()

        assert(result.exit_code == 0)

    @patch('floyd.cli.data.DataClient.get')
    @patch('floyd.cli.data.DataClient.delete', return_value=True)
    def test_with_multiple_ids_and_yes_option(self, delete_data, get_data):
        id_1, id_2, id_3 = '1', '2', '3'
        result = self.runner.invoke(delete, ['-y', id_1, id_2, id_3])

        # Doesn't send a get before attempting to delete
        get_data.assert_not_called()

        # Trigger a delete for each id
        calls = [call(id_1), call(id_2), call(id_3)]
        delete_data.assert_has_calls(calls, any_order=True)

        assert(result.exit_code == 0)

    @patch('floyd.cli.data.DataClient.get')
    @patch('floyd.cli.data.DataClient.delete', return_value=True)
    def test_delete_without_yes_option(self, delete_data, get_data):
        id_1, id_2, id_3 = '1', '2', '3'

        # Tell prompt to skip id_1 and id_3
        result = self.runner.invoke(delete,
                                    [id_1, id_2, id_3],
                                    input='n\nY\nn\n')

        # Doesn't send a get before attempting to delete
        get_data.assert_not_called()

        # Calls delete for only id_2
        delete_data.assert_called_once_with(id_2)

        assert(result.exit_code == 0)

    @patch('floyd.cli.data.DataClient.get')
    @patch('floyd.cli.data.DataClient.delete', return_value=False)
    def test_failed_delete(self, delete_data, get_data):
        id_1, id_2, id_3 = '1', '2', '3'
        result = self.runner.invoke(delete, ['-y', id_1, id_2, id_3])

        # Doesn't send a get before attempting to delete
        get_data.assert_not_called()

        # Trigger a delete for each id, even though each delete
        # fails. All deletes are attempted regardless of previous failures.
        calls = [call(id_1), call(id_2), call(id_3)]
        delete_data.assert_has_calls(calls, any_order=True)

        # Exit 1 for failed deletes
        assert(result.exit_code == 1)
