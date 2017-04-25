from click.testing import CliRunner
import unittest
from mock import patch, call

import floyd
from floyd.cli.experiment import delete
from tests.cli.experiment.mocks import mock_exp, mock_running_exp, \
                                       mock_queued_exp, mock_task_inst


class TestExperiementDelete(unittest.TestCase):
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

    @patch('floyd.cli.experiment.TaskInstanceClient.get',
           side_effect=mock_task_inst)
    @patch('floyd.cli.experiment.ModuleClient.delete')
    @patch('floyd.cli.experiment.ExperimentClient.get', side_effect=mock_exp)
    @patch('floyd.cli.experiment.ExperimentClient.delete')
    def test_with_multiple_ids_and_yes_option(self,
                                              delete_experiment,
                                              get_experiment,
                                              delete_module,
                                              get_task_instance):
        id_1, id_2, id_3 = '1', '2', '3'
        result = self.runner.invoke(delete, ['-y', id_1, id_2, id_3])

        # Trigger a get and a delete for each id
        calls = [call(id_1), call(id_2), call(id_3)]
        get_experiment.assert_has_calls(calls, any_order=True)
        get_task_instance.assert_called()
        delete_module.assert_called()
        delete_experiment.assert_has_calls(calls, any_order=True)

        assert(result.exit_code == 0)

    @patch('floyd.cli.experiment.TaskInstanceClient.get',
           side_effect=mock_task_inst)
    @patch('floyd.cli.experiment.ModuleClient')
    @patch('floyd.cli.experiment.ExperimentClient.get', side_effect=mock_exp)
    @patch('floyd.cli.experiment.ExperimentClient.delete')
    def test_delete_without_yes_option(self,
                                       delete_experiment,
                                       get_experiment,
                                       delete_module, get_task_instance):
        id_1, id_2, id_3 = '1', '2', '3'

        # Tell prompt to skip id_1 and id_3
        result = self.runner.invoke(delete,
                                    [id_1, id_2, id_3],
                                    input='n\nY\nn\n')

        # Triggers a get for all ids
        calls = [call(id_1), call(id_2), call(id_3)]
        get_experiment.assert_has_calls(calls, any_order=True)
        get_task_instance.assert_called()

        # Calls delete for only id_2
        delete_experiment.assert_called_once_with(id_2)
        delete_module.assert_called_once()

        assert(result.exit_code == 0)

    @patch('floyd.cli.experiment.TaskInstanceClient.get',
           side_effect=mock_task_inst)
    @patch('floyd.cli.experiment.ModuleClient')
    @patch('floyd.cli.experiment.ExperimentClient.get',
           side_effect=mock_queued_exp)
    @patch('floyd.cli.experiment.ExperimentClient.delete')
    def test_delete_with_queued_experiments(self,
                                            delete_experiment,
                                            get_experiment,
                                            delete_module,
                                            get_task_instance):
        id_1, id_2 = '1', '2'

        result = self.runner.invoke(delete, ['-y', id_1, id_2])

        # Triggers a get for all ids
        calls = [call(id_1), call(id_2)]
        get_experiment.assert_has_calls(calls, any_order=True)
        get_task_instance.assert_called()

        # Does not attempt to delete
        delete_module.assert_not_called()
        delete_experiment.assert_not_called()

        assert(result.exit_code == 0)

    @patch('floyd.cli.experiment.TaskInstanceClient.get',
           side_effect=mock_task_inst)
    @patch('floyd.cli.experiment.ModuleClient')
    @patch('floyd.cli.experiment.ExperimentClient.get',
           side_effect=mock_running_exp)
    @patch('floyd.cli.experiment.ExperimentClient.delete')
    def test_delete_with_running_experiments(self,
                                             delete_experiment,
                                             get_experiment,
                                             delete_module,
                                             get_task_instance):
        id_1, id_2 = '1', '2'

        result = self.runner.invoke(delete, ['-y', id_1, id_2])

        # Triggers a get for all ids
        calls = [call(id_1), call(id_2)]
        get_experiment.assert_has_calls(calls, any_order=True)
        get_task_instance.assert_called()

        # Does not attempt to delete
        delete_module.assert_not_called()
        delete_experiment.assert_not_called()

        assert(result.exit_code == 0)
