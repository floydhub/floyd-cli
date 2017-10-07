import unittest
from mock import patch
from floyd.manager.auth_config import AuthConfigManager


class TestAuthConfig(unittest.TestCase):
    @patch('floyd.manager.auth_config.os.path.expanduser')
    @patch('floyd.model.access_token.sys.exit')
    def test_auth_config(self, sys_exit, expanduser):
        import base64
        from floyd.model.access_token import assert_token_not_expired, AccessToken
        expanduser.return_value = '/tmp/.floydconfig'
        mock_token = 'a.' + base64.b64encode('{"exp": 1}'.encode('ascii')).decode('ascii') + '.c'
        access_token = AccessToken('foo', mock_token)
        AuthConfigManager.set_access_token(access_token)
        assert AuthConfigManager.get_access_token().token == mock_token
