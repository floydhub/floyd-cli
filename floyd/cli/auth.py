import click
import getpass
import sys

import floyd
from floyd.client.auth import AuthClient
from floyd.manager.auth_config import AuthConfigManager
from floyd.manager.login import (
    has_browser,
    wait_for_apikey,
)
from floyd.model.access_token import AccessToken
from floyd.model.credentials import Credentials
from floyd.log import logger as floyd_logger


def get_access_code_from_password(username, password):
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
    access_token = AuthClient().login(login_credentials)
    if not access_token:
        floyd_logger.info("Failed to login")
        sys.exit(1)

    return access_token


def manual_login_success(token, username, password):
    if token:
        # Login using authentication token
        floyd_logger.info(
            "Please paste the authentication token from %s/settings/security.",
            floyd.floyd_web_host)
        access_token = click.prompt('This is an invisible field. Paste token and press ENTER', type=str, hide_input=True)
        access_token = access_token.strip()

        if not access_token:
            floyd_logger.info("Empty token received. Make sure your shell is handling the token appropriately.")
            floyd_logger.info("See docs for help: http://docs.floydhub.com/faqs/authentication/")
            return

    elif username or password:
        access_token = get_access_code_from_password(username, password)
    else:
        return False

    user = AuthClient().get_user(access_token)
    AuthConfigManager.set_access_token(
        AccessToken(username=user.username,
                    token=access_token))
    floyd_logger.info("Login Successful as %s", user.username)
    return True


@click.command()
@click.option('--token', is_flag=True, default=False, help='Just enter token')
@click.option('--apikey', '-k', help='Api Key')
@click.option('--username', '-u', help='FloydHub username')
@click.option('--password', '-p', help='FloydHub password')
def login(token, apikey, username, password):
    """
    Login to FloydHub.
    """
    if manual_login_success(token, username, password):
        return

    if not apikey:
        if has_browser():
            apikey = wait_for_apikey()
        else:
            floyd_logger.error(
                "No browser found, please login manually by creating login key at %s/settings/apikey.",
                floyd.floyd_web_host)
            sys.exit(1)

    if apikey:
        user = AuthClient().get_user(apikey, is_apikey=True)
        AuthConfigManager.set_apikey(username=user.username, apikey=apikey)
        floyd_logger.info("Login Successful as %s", user.username)
    else:
        floyd_logger.error("Login failed, please see --help for other login options.")


@click.command()
def logout():
    """
    Logout of FloydHub.
    """
    AuthConfigManager.purge_access_token()
