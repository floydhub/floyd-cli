from click.testing import CliRunner
import unittest

from tests.cli import assert_exit_code
from floyd.cli.auth import login


class TestAuthClient(unittest.TestCase):
    """
    Tests Experiment CLI functionality
    """
    def setUp(self):
        self.runner = CliRunner()

    def test_login_help(self):
        result = self.runner.invoke(login, ['--help'])
        assert_exit_code(result, 0)
