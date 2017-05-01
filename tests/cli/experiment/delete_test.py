from click.testing import CliRunner
import unittest
from mock import patch, call

from floyd.cli.experiment import delete
from tests.cli.mocks import mock_exp, mock_task_inst


class TestExperimentDelete(unittest.TestCase):
    """
    Tests Experiment CLI delete functionality `floyd delete`
    """
    def setUp(self):
        self.runner = CliRunner()

    @patch('floyd.cli.experiment.TaskInstanceClient')
    @patch('floyd.cli.experiment.ModuleClient')
    @patch('floyd.cli.experiment.ExperimentClient')
    def test_with_no_arguments(self, *api_clients):
        result = self.runner.invoke(delete)

        # No calls to API clients, exit 0
        for client in api_clients:
            client.assert_not_called()

        assert(result.exit_code == 0)

    @patch('floyd.cli.experiment.TaskInstanceClient')
    @patch('floyd.cli.experiment.ModuleClient')
    @patch('floyd.cli.experiment.ExperimentClient.get', side_effect=mock_exp)
    @patch('floyd.cli.experiment.ExperimentClient.delete')
    def test_with_multiple_ids_and_yes_option(self,
                                              delete_experiment,
                                              get_experiment,
                                              module_client,
                                              task_instance_client):
        id_1, id_2, id_3 = '1', '2', '3'
        result = self.runner.invoke(delete, ['-y', id_1, id_2, id_3])

        # Trigger a get and a delete for each id
        calls = [call(id_1), call(id_2), call(id_3)]
        get_experiment.assert_has_calls(calls, any_order=True)
        delete_experiment.assert_has_calls(calls, any_order=True)

        assert(result.exit_code == 0)

    @patch('floyd.cli.experiment.TaskInstanceClient')
    @patch('floyd.cli.experiment.ModuleClient')
    @patch('floyd.cli.experiment.ExperimentClient.get', side_effect=mock_exp)
    @patch('floyd.cli.experiment.ExperimentClient.delete')
    def test_delete_without_yes_option(self,
                                       delete_experiment,
                                       get_experiment,
                                       module_client,
                                       task_instance_client):
        id_1, id_2, id_3 = '1', '2', '3'

        # Tell prompt to skip id_1 and id_3
        result = self.runner.invoke(delete,
                                    [id_1, id_2, id_3],
                                    input='n\nY\nn\n')

        # Triggers a get for all ids
        calls = [call(id_1), call(id_2), call(id_3)]
        get_experiment.assert_has_calls(calls, any_order=True)

        # Calls delete for only id_2
        delete_experiment.assert_called_once_with(id_2)

        # Does not call TaskInstanceClient or ModuleClient
        task_instance_client.assert_not_called()
        module_client.assert_not_called()

        assert(result.exit_code == 0)

    @patch('floyd.cli.experiment.TaskInstanceClient')
    @patch('floyd.cli.experiment.ModuleClient')
    @patch('floyd.cli.experiment.ExperimentClient.get', side_effect=mock_exp)
    @patch('floyd.cli.experiment.ExperimentClient.delete', return_value=False)
    def test_failed_delete(self, delete_experiment, get_experiment,
                           task_instance_client, module_client):
        id_1, id_2, id_3 = '1', '2', '3'
        result = self.runner.invoke(delete, ['-y', id_1, id_2, id_3])

        # Trigger a get and a delete for each id, even though each delete
        # fails. All deletes are attempted regardless of previous failures.
        calls = [call(id_1), call(id_2), call(id_3)]
        get_experiment.assert_has_calls(calls, any_order=True)
        delete_experiment.assert_has_calls(calls, any_order=True)

        # Exit 1 for failed deletes
        assert(result.exit_code == 1)

    @patch('floyd.cli.experiment.TaskInstanceClient.get', return_value=False)
    @patch('floyd.cli.experiment.get_module_task_instance_id', return_value='123')
    @patch('floyd.cli.experiment.ModuleClient')
    @patch('floyd.cli.experiment.ExperimentClient')
    def test_with_no_found_task_instance(self,
                                         experiment_client,
                                         module_client,
                                         get_module_task_instance_id,
                                         get_task_instance):
        id_1 = '1'
        result = self.runner.invoke(delete, ['-y', id_1])

        # If a task instance is not found, ModuleClient is not called
        get_module_task_instance_id.assert_called_once()
        get_task_instance.assert_called_once_with('123')
        module_client.assert_not_called()

        # Exit 0 for successful experiment delete
        assert(result.exit_code == 0)

    @patch('floyd.cli.experiment.TaskInstanceClient.get', side_effect=mock_task_inst)
    @patch('floyd.cli.experiment.get_module_task_instance_id', return_value='123')
    @patch('floyd.cli.experiment.ModuleClient.delete')
    @patch('floyd.cli.experiment.ExperimentClient')
    def test_with_found_task_instance(self,
                                      experiment_client,
                                      delete_module,
                                      get_module_task_instance_id,
                                      get_task_instance):
        id_1 = '1'
        result = self.runner.invoke(delete, ['-y', id_1])

        # Get the module_id of the experiment's task instance and call delete
        # on it. '999999' is the module_id of the mocked TaskInstance
        get_module_task_instance_id.assert_called_once()
        get_task_instance.assert_called_once_with('123')
        delete_module.assert_called_once_with('999999')

        # Exit 0 for successful experiment delete
        assert(result.exit_code == 0)
