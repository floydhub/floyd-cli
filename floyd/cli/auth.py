import click
import getpass
import sys

import floyd
from floyd.client.auth import AuthClient
from floyd.manager.auth_config import AuthConfigManager
from floyd.model.access_token import AccessToken
from floyd.model.credentials import Credentials
from floyd.log import logger as floyd_logger


@click.command()
@click.option('--token', is_flag=True, default=False, help='Just enter token')
@click.option('--apikey', '-k', default=None, help='Api Key')
@click.option('--username', '-u', default=None, help='FloydHub username')
@click.option('--password', '-p', default=None, help='FloydHub password')
def login(token, apikey, username, password):
    """
    Login to FloydHub.
    """
    if apikey:
        user = AuthClient().get_user(apikey, True)
        AuthConfigManager.set_apikey(username=user.username, apikey=apikey)
        floyd_logger.info("Login Successful as %s", user.username)
        return

    elif token:
        # Login using authentication token
        floyd_logger.info(
            "Please paste the authentication token from {}/settings/security.".format(floyd.floyd_web_host))
        access_code = click.prompt('This is an invisible field. Paste token and press ENTER', type=str, hide_input=True)
        access_code = access_code.strip()

        if not access_code:
            floyd_logger.info("Empty token received. Make sure your shell is handling the token appropriately.")
            floyd_logger.info("See docs for help: http://docs.floydhub.com/faqs/authentication/")
            return

        access_code = access_code.strip(" ")

    else:
        # Use username / password login
        floyd_logger.info("Login with your FloydHub username and password to run jobs.")

        if not username:
            username = click.prompt('Username', type=str, default=getpass.getuser())
            username = username.strip()
            if not username:
                floyd_logger.info('You entered an empty string. Please make sure you enter your username correctly.')
                sys.exit(1)

        if not password:
            password = click.prompt('Password', type=str, hide_input=True)
            password = password.strip()
            if not password:
                floyd_logger.info('You entered an empty string. Please make sure you enter your password correctly.')
                sys.exit(1)

        login_credentials = Credentials(username=username,
                                        password=password)
        access_code = AuthClient().login(login_credentials)
        if not access_code:
            floyd_logger.info("Failed to login")
            return

    user = AuthClient().get_user(access_code)
    access_token = AccessToken(username=user.username,
                               token=access_code)
    AuthConfigManager.set_access_token(access_token)
    floyd_logger.info("Login Successful as %s", user.username)


@click.command()
def logout():
    """
    Logout of FloydHub.
    """
    AuthConfigManager.purge_access_token()
