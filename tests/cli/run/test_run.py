from click.testing import CliRunner
import unittest
from mock import patch

from floyd.cli.run import run
from tests.cli.mocks import mock_access_token, mock_experiment_config


class TestExperimentRun(unittest.TestCase):
    """
    Tests for `floyd run` functionality.
    """
    def setUp(self):
        self.runner = CliRunner()

    @patch('floyd.cli.run.EnvClient.get_all', return_value={'cpu': {'foo': 'bar'}})
    @patch('floyd.cli.run.AuthConfigManager.get_access_token', side_effect=mock_access_token)
    @patch('floyd.cli.run.ExperimentConfigManager.get_config', side_effect=mock_experiment_config)
    @patch('floyd.cli.run.ExperimentConfigManager.set_config')
    @patch('floyd.cli.run.ModuleClient.create', return_value='module_id')
    @patch('floyd.cli.run.ExperimentClient.create', return_value='expt_id')
    @patch('floyd.cli.run.ProjectClient.exists', return_value=True)
    def test_with_no_data(self,
                          create_experiment,
                          create_module,
                          set_config,
                          get_config,
                          get_access_token,
                          get_all_env,
                          exists):
        """
        Simple experiment with no data attached
        """
        result = self.runner.invoke(run, ['command'])
        assert(result.exit_code == 0)

    @patch('floyd.cli.run.AuthConfigManager.get_access_token', side_effect=mock_access_token)
    @patch('floyd.cli.run.ExperimentConfigManager.get_config', side_effect=mock_experiment_config)
    @patch('floyd.cli.run.ExperimentConfigManager.set_config')
    @patch('floyd.cli.run.ModuleClient.create', return_value='module_id')
    @patch('floyd.cli.run.ExperimentClient.create', return_value='expt_id')
    @patch('floyd.cli.run.ProjectClient.exists', return_value=True)
    def test_with_multiple_data_ids(self,
                                    create_experiment,
                                    create_module,
                                    set_config,
                                    get_config,
                                    get_access_token,
                                    exists):
        """
        Simple experiment with no data attached
        """
        result = self.runner.invoke(run, ['command', '--data', 'data-id1', '--data', 'data-id2'])
        assert(result.exit_code == 0)
