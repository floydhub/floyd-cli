from click.testing import CliRunner
import unittest
from mock import patch

from floyd.cli.run import run, get_command_line
from tests.cli.mocks import mock_access_token, mock_experiment_config


class TestExperimentRun(unittest.TestCase):
    """
    Tests for `floyd run` functionality.
    """
    def setUp(self):
        self.runner = CliRunner()

    @patch('floyd.model.access_token.assert_token_not_expired')
    @patch('floyd.cli.run.EnvClient.get_all', return_value={'cpu': {'default': 'bar'}})
    @patch('floyd.cli.run.AuthConfigManager.get_access_token', side_effect=mock_access_token)
    @patch('floyd.cli.run.ExperimentConfigManager.get_config', side_effect=mock_experiment_config)
    @patch('floyd.cli.run.ExperimentConfigManager.set_config')
    @patch('floyd.cli.run.ModuleClient.create', return_value='module_id')
    @patch('floyd.cli.run.ExperimentClient')
    @patch('floyd.cli.run.ProjectClient.exists', return_value=True)
    def test_with_no_data(self,
                          exists,
                          expt_client,
                          create_module,
                          set_config,
                          get_config,
                          get_access_token,
                          get_all_env,
                          assert_token_not_expired):
        """
        Simple experiment with no data attached
        """
        result = self.runner.invoke(run, ['command'])
        assert(result.exit_code == 0)

    @patch('floyd.model.access_token.assert_token_not_expired')
    @patch('floyd.cli.run.DataClient.get')
    @patch('floyd.cli.run.EnvClient.get_all', return_value={'cpu': {'default': 'bar'}})
    @patch('floyd.cli.run.AuthConfigManager.get_access_token', side_effect=mock_access_token)
    @patch('floyd.cli.run.ExperimentConfigManager.get_config', side_effect=mock_experiment_config)
    @patch('floyd.cli.run.ExperimentConfigManager.set_config')
    @patch('floyd.cli.run.ModuleClient.create', return_value='module_id')
    @patch('floyd.cli.run.ExperimentClient')
    @patch('floyd.cli.run.ProjectClient.exists', return_value=True)
    def test_with_multiple_data_ids(self,
                                    exists,
                                    expt_client,
                                    create_module,
                                    set_config,
                                    get_config,
                                    get_access_token,
                                    env_get_all,
                                    data_get,
                                    assert_token_not_expired):
        """
        Simple experiment with no data attached
        """
        data_get.return_value.id = 'data_id'
        result = self.runner.invoke(run, ['command', '--data', 'data-id1', '--data', 'data-id2'])
        assert(result.exit_code == 0)

    def test_get_command_line(self):
        re = get_command_line(
            instance_type='g1p',
            env='pytorch-2.0:py2',
            message='test\' message',
            data=['foo:input'],
            mode='job',
            open_notebook=False,
            tensorboard=True,
            command_str='echo hello'
        )
        assert re == 'floyd run --gpu+ --env pytorch-2.0:py2 --message \'test\'"\'"\' message\' --data foo:input --tensorboard \'echo hello\''

        re = get_command_line(
            instance_type='c1',
            env='tensorflow',
            message=None,
            data=['foo:input', 'bar'],
            mode='jupyter',
            open_notebook=True,
            tensorboard=False,
            command_str='echo \'hello'
        )
        assert re == 'floyd run --cpu --env tensorflow --data foo:input --data bar --mode jupyter'

        re = get_command_line(
            instance_type='g1',
            env='tensorflow',
            message=None,
            data=['foo:input'],
            mode='job',
            open_notebook=False,
            tensorboard=True,
            command_str='echo hello > /output'
        )
        assert re == 'floyd run --gpu --env tensorflow --data foo:input --tensorboard \'echo hello > /output\''
