import unittest
from mock import patch


class TestAccessToken(unittest.TestCase):
    def test_assert_token_not_expired(self):
        import base64
        from floyd.model.access_token import assert_token_not_expired

        # user input from click.prompt is of type string
        assert_token_not_expired(
            'a.' + base64.b64encode('{"exp": 10000000000000000}'.encode('ascii')).decode('ascii') + '.c')
