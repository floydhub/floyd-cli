from click.testing import CliRunner
import unittest
from mock import patch, Mock, PropertyMock

from floyd.cli.version import upgrade

class TestFloydVersion(unittest.TestCase):
    """
    Tests cli utils helper functions
    """

    def setUp(self):
        self.runner = CliRunner()

    @patch('floyd.cli.version.pip_upgrade')
    @patch('floyd.cli.version.conda_upgrade')
    @patch('floyd.cli.utils.sys')
    def test_floyd_upgrade_with_standard_python(self, mock_sys, conda_upgrade, pip_upgrade):
        mock_sys.version = '2.7.13 (default, Jan 19 2017, 14:48:08) \n[GCC 6.3.0 20170118]'

        self.runner.invoke(upgrade)

        conda_upgrade.assert_not_called()
        pip_upgrade.assert_called_once()

    @patch('floyd.cli.version.pip_upgrade')
    @patch('floyd.cli.version.conda_upgrade')
    @patch('floyd.cli.utils.sys')
    def test_floyd_upgrade_with_anaconda_python(self, mock_sys, conda_upgrade, pip_upgrade):
        mock_sys.version = '3.6.3 |Anaconda, Inc.| (default, Oct 13 2017, 12:02:49) \n[GCC 7.2.0]'

        self.runner.invoke(upgrade)

        pip_upgrade.assert_not_called()
        conda_upgrade.assert_called_once()
