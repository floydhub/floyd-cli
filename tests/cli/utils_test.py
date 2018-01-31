import unittest

from mock import patch

from tests.cli.mocks import mock_access_token, mock_experiment_config

class TestCliUtil(unittest.TestCase):
    """
    Tests cli utils helper functions
    """
    @patch('floyd.cli.utils.current_username', return_value='pete')
    @patch('floyd.cli.utils.current_dataset_name', return_value='test_dataset')
    @patch('floyd.cli.utils.current_project_name', return_value='my_expt')
    def test_normalize_data_name(self, _0, _1, _2):
        from floyd.cli.utils import normalize_data_name
        assert normalize_data_name('foo/bar/1') == 'foo/datasets/bar/1'
        assert normalize_data_name('foo/datasets/bar/1') == 'foo/datasets/bar/1'
        assert normalize_data_name('foo/bar/1/output') == 'foo/projects/bar/1/output'
        assert normalize_data_name('foo/projects/bar/1/output') == 'foo/projects/bar/1/output'
        # Make sure that the current_username and current_project_name are
        # honored:
        assert normalize_data_name('1') == 'pete/datasets/test_dataset/1'
        assert normalize_data_name('mnist/3') == 'pete/datasets/mnist/3'
        assert normalize_data_name('foo/mnist/3') == 'foo/datasets/mnist/3'

        # current_username and current_project_name are overridden with the
        # second and third args if passed
        assert normalize_data_name('bar/1', 'yoyo') == 'yoyo/datasets/bar/1'
        assert normalize_data_name('1', 'yoyo', 'ma') == 'yoyo/datasets/ma/1'

        # Full job names are returned unchanged
        assert normalize_data_name('foo/projects/bar/1') == 'foo/datasets/bar/1'

        # If no job number is passed, it is not used
        assert normalize_data_name('foo/datasets/bar') == 'foo/datasets/bar'


    @patch('floyd.cli.utils.current_username', return_value='pete')
    @patch('floyd.cli.utils.current_project_name', return_value='test_proj')
    @patch('floyd.cli.utils.get_latest_job_name_for_project', return_value='TEST')
    def test_normalize_job_name(self, _0, _1, _2):
        from floyd.cli.utils import normalize_job_name

        # Make sure that the current_username and current_project_name are
        # honored:
        assert normalize_job_name('1') == 'pete/projects/test_proj/1'
        assert normalize_job_name('mnist/3') == 'pete/projects/mnist/3'
        assert normalize_job_name('foo/mnist/3') == 'foo/projects/mnist/3'

        # current_username and current_project_name are overridden with the
        # second and third args if passed
        assert normalize_job_name('bar/1', 'yoyo') == 'yoyo/projects/bar/1'
        assert normalize_job_name('1', 'yoyo', 'ma') == 'yoyo/projects/ma/1'

        # Full job names are returned unchanged
        assert normalize_job_name('foo/projects/bar/1') == 'foo/projects/bar/1'

        # If no job number is passed, get_last_job_name is used
        assert normalize_job_name('foo/projects/bar') == 'TEST'




    @patch('floyd.cli.utils.AuthConfigManager.get_access_token', side_effect=mock_access_token)
    def test_current_username(self, token):
        from floyd.cli.utils import current_username

        # Returns the username of AuthConfigManager().get_access_token()
        assert current_username() == token().username


    @patch('floyd.cli.utils.ExperimentConfigManager.get_config', side_effect=mock_experiment_config)
    def test_current_project_name(self, expt_config):
        from floyd.cli.utils import current_project_name

        # Returns the name of ExperimentConfigManager().get_config()
        assert current_project_name() == expt_config().name
