import unittest
from mock import patch
from floyd.manager.data_config import DataConfig
from tests.cli.mocks import mock_access_token, mock_experiment_config


data_config = DataConfig('test_dataset', namespace='pete')


class TestCliUtil(unittest.TestCase):
    """
    Tests cli utils helper functions
    """
    @patch('floyd.manager.experiment_config.ExperimentConfigManager.get_config')
    @patch('floyd.cli.utils.current_username', return_value='pete')
    @patch('floyd.cli.utils.current_dataset_name', return_value='test_dataset')
    @patch('floyd.cli.utils.current_project_name', return_value='my_expt')
    @patch('floyd.cli.utils.DataConfigManager.get_config', return_value=data_config)
    def test_normalize_data_name(self, _0, _1, _2, _3, mock_get_config):
        mock_get_config.return_value.namespace = None
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
        assert normalize_data_name('foo/projects/bar/1') == 'foo/projects/bar/1'

        # If no job number is passed, it is not used
        assert normalize_data_name('foo/datasets/bar') == 'foo/datasets/bar'

    @patch('floyd.manager.experiment_config.ExperimentConfigManager.get_config')
    @patch('floyd.cli.utils.current_username', return_value='pete')
    @patch('floyd.cli.utils.current_project_name', return_value='test_proj')
    @patch('floyd.cli.utils.get_latest_job_name_for_project', return_value='TEST')
    def test_normalize_job_name(self, _0, _1, _2, mock_get_config):
        mock_get_config.return_value.namespace = None

        from floyd.cli.utils import normalize_job_name

        # Make sure that the current_username and current_project_name are
        # honored:
        assert normalize_job_name('1') == 'pete/projects/test_proj/1'
        assert normalize_job_name('mnist/3') == 'pete/projects/mnist/3'
        assert normalize_job_name('foo/mnist/3') == 'foo/projects/mnist/3'

        # current_username and current_project_name are overridden with the
        # second and third args if passed
        assert normalize_job_name('bar/1', 'yoyo', use_config=False) == 'yoyo/projects/bar/1'
        assert normalize_job_name('1', 'yoyo', 'ma', use_config=False) == 'yoyo/projects/ma/1'

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

    @patch('floyd.cli.utils.current_username', return_value='pete')
    def test_get_namespace_from_name(self, _0):
        """
        Test Regex for args of dataset and project initialization
        """
        from floyd.cli.utils import get_namespace_from_name
        # PATTERN: <dataset_or_project_name>
        assert get_namespace_from_name('test') == ('pete', 'test')

        # PATTERN: <namespace>/[dataset|project]/<dataset_or_project_name>
        assert get_namespace_from_name('fo.o_user/datasets/test_1') == ('fo.o_user', 'test_1')
        assert get_namespace_from_name('fo.o_user/projects/test_1') == ('fo.o_user', 'test_1')

        # PATTERN: <namespace>/<dataset_or_project_name>
        assert get_namespace_from_name('fo.o_user/test_1-1') == ('fo.o_user', 'test_1-1')

        # BAD PATTERN: Bad argument (/)
        with self.assertRaises(SystemExit) as cm:
            get_namespace_from_name('/')

        error = ("Argument '/' doesn't match any recognized pattern:\n"
                 "\tfloyd [data] init <project_or_dataset_name>\n"
                 "\tfloyd [data] init <namespace>/<project_or_dataset_name>\n"
                 "\tfloyd [data] init <namespace>/[projects|dataset]/<project_or_dataset_name>\n"
                 "\n Note: Argument can only contain alphanumeric, hyphen-minus '-' , underscore '_' and dot '.' characters."
                 )
        self.assertEqual(cm.exception.code, error)

        # BAD PATTERN: Characters not allowed (:?)
        with self.assertRaises(SystemExit) as cm:
            get_namespace_from_name('test_:?1-1')

        error = ("Argument 'test_:?1-1' doesn't match any recognized pattern:\n"
                 "\tfloyd [data] init <project_or_dataset_name>\n"
                 "\tfloyd [data] init <namespace>/<project_or_dataset_name>\n"
                 "\tfloyd [data] init <namespace>/[projects|dataset]/<project_or_dataset_name>\n"
                 "\n Note: Argument can only contain alphanumeric, hyphen-minus '-' , underscore '_' and dot '.' characters."
                 )
        self.assertEqual(cm.exception.code, error)
