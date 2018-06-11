from click.testing import CliRunner
import unittest
from mock import patch, call

from floyd.cli.data import delete
from floyd.model.experiment_config import ExperimentConfig
from tests.cli.data.mocks import mock_data, mock_project_client, mock_access_token
from tests.cli.mocks import mock_data_config
from tests.cli import assert_exit_code


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

        assert_exit_code(result, 0)

    @patch('floyd.manager.data_config.DataConfigManager.get_config', side_effect=mock_data_config)
    @patch('floyd.manager.experiment_config.ExperimentConfigManager.get_config', return_value=ExperimentConfig('foo', '12345'))
    @patch('floyd.client.project.ProjectClient', side_effect=mock_project_client)
    @patch('floyd.manager.auth_config.AuthConfigManager.get_access_token', side_effect=mock_access_token)
    @patch('floyd.manager.auth_config.AuthConfigManager.get_auth_header', return_value="Bearer " + mock_access_token().token)
    @patch('floyd.model.access_token.assert_token_not_expired')
    @patch('floyd.cli.data.DataClient.get', side_effect=mock_data)
    @patch('floyd.cli.data.DataClient.delete', return_value=True)
    def test_with_multiple_ids_and_yes_option(self,
                                              delete_data,
                                              get_data,
                                              assert_token_not_expired,
                                              get_auth_header,
                                              get_access_token,
                                              get_project,
                                              get_expt_config,
                                              get_data_config):
        id_1 = 'mckay/datasets/foo/1'
        id_2 = 'mckay/datasets/bar/1'
        id_3 = 'mckay/datasets/foo/1'

        result = self.runner.invoke(delete, ['-y', id_1, id_2, id_3])

        assert_exit_code(result, 0)
        # Trigger a get and a delete for each id
        calls = [call(id_1), call(id_2), call(id_3)]
        get_data.assert_has_calls(calls, any_order=True)
        delete_data.assert_has_calls(calls, any_order=True)


    @patch('floyd.manager.data_config.DataConfigManager.get_config', side_effect=mock_data_config)
    @patch('floyd.manager.experiment_config.ExperimentConfigManager.get_config', return_value=ExperimentConfig('foo', '12345'))
    @patch('floyd.client.project.ProjectClient', side_effect=mock_project_client)
    @patch('floyd.manager.auth_config.AuthConfigManager.get_access_token')
    @patch('floyd.manager.auth_config.AuthConfigManager.get_auth_header')
    @patch('floyd.model.access_token.assert_token_not_expired')
    @patch('floyd.cli.data.DataClient.get', side_effect=mock_data)
    @patch('floyd.cli.data.DataClient.delete', return_value=True)
    def test_delete_without_yes_option(self,
                                       delete_data,
                                       get_data,
                                       assert_token_not_expired,
                                       get_auth_header,
                                       get_access_token,
                                       project_client,
                                       get_expt_config,
                                       get_data_config):
        id_1 = 'mckay/datasets/foo/1'
        id_2 = 'mckay/datasets/bar/1'
        id_3 = 'mckay/datasets/foo/1'

        # Tell prompt to skip id_1 and id_3
        result = self.runner.invoke(delete,
                                    [id_1, id_2, id_3],
                                    input='n\nY\nn\n')

        # Triggers a get for all ids
        calls = [call(id_1), call(id_2), call(id_3)]
        get_data.assert_has_calls(calls, any_order=True)

        # Calls delete for only id_2
        delete_data.assert_called_once_with(id_2)

        assert_exit_code(result, 0)

    @patch('floyd.manager.data_config.DataConfigManager.get_config', side_effect=mock_data_config)
    @patch('floyd.manager.experiment_config.ExperimentConfigManager.get_config', return_value=ExperimentConfig('foo', '12345'))
    @patch('floyd.client.project.ProjectClient', side_effect=mock_project_client)
    @patch('floyd.manager.auth_config.AuthConfigManager.get_access_token')
    @patch('floyd.manager.auth_config.AuthConfigManager.get_auth_header')
    @patch('floyd.model.access_token.assert_token_not_expired')
    @patch('floyd.cli.data.DataClient.get', side_effect=mock_data)
    @patch('floyd.cli.data.DataClient.delete', return_value=False)
    def test_failed_delete(self,
                           delete_data,
                           get_data,
                           assert_token_not_expired,
                           get_auth_header,
                           get_access_token,
                           project_client,
                           get_expt_config,
                           get_data_config):
        id_1 = 'mckay/datasets/foo/1'
        id_2 = 'mckay/datasets/bar/1'
        id_3 = 'mckay/datasets/foo/1'

        result = self.runner.invoke(delete, ['-y', id_1, id_2, id_3])

        # Trigger a get and a delete for each id, even though each delete
        # fails. All deletes are attempted regardless of previous failures.
        calls = [call(id_1), call(id_2), call(id_3)]
        get_data.assert_has_calls(calls, any_order=True)
        delete_data.assert_has_calls(calls, any_order=True)

        # Exit 1 for failed deletes
        assert_exit_code(result, 1)

    @patch('floyd.manager.data_config.DataConfigManager.get_config', side_effect=mock_data_config)
    @patch('floyd.manager.experiment_config.ExperimentConfigManager.get_config', return_value=ExperimentConfig('foo', '12345'))
    @patch('floyd.manager.auth_config.AuthConfigManager.get_access_token')
    @patch('floyd.manager.auth_config.AuthConfigManager.get_auth_header')
    @patch('floyd.model.access_token.assert_token_not_expired')
    @patch('floyd.cli.data.DataClient.get', return_value=None)
    @patch('floyd.cli.data.DataClient.delete')
    def test_failed_get(self,
                        delete_data,
                        get_data,
                        assert_token_not_expired,
                        get_auth_header,
                        get_access_token,
                        get_expt_config,
                        get_data_config):
        id_1 = 'mckay/datasets/foo/1'
        id_2 = 'mckay/datasets/bar/1'
        id_3 = 'mckay/datasets/foo/1'

        result = self.runner.invoke(delete, ['-y', id_1, id_2, id_3])

        # Trigger a get for each id, even though each fails. (No early exit)
        calls = [call(id_1), call(id_2), call(id_3)]
        get_data.assert_has_calls(calls, any_order=True)

        # Deletes are not triggered for ids that are not found
        delete_data.assert_not_called()

        # Exit 1 for failed get requests
        assert_exit_code(result, 1)
