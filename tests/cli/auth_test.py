from click.testing import CliRunner
import unittest

from floyd.cli.auth import login


class TestAuthClient(unittest.TestCase):
    """
    Tests Experiment CLI functionality
    """
    def setUp(self):
        self.runner = CliRunner()

    def test_login(self):
        result = self.runner.invoke(login, ['test19', 'test'])
        assert(result.exit_code == 0)
