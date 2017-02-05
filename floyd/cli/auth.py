import click
import webbrowser

import floyd
from floyd.client.auth import AuthClient
from floyd.manager.auth_config import AuthConfigManager
from floyd.model.access_token import AccessToken
from floyd.log import logger as floyd_logger


@click.command()
def login():
    """
    Log into Floyd via Auth0.
    """
    cli_info_url = "{}/cli".format(floyd.floyd_web_host)
    if not click.confirm('Access token page will now open in your browser. Continue?'):
        return

    webbrowser.open(cli_info_url)
    access_code = click.prompt('Please paste the code here', type=str)

    user = AuthClient().get_user(access_code)
    access_token = AccessToken(username=user.username,
                               token=access_code)
    AuthConfigManager.set_access_token(access_token)
    floyd_logger.info("Login Successful")


@click.command()
def logout():
    """
    Logout of Floyd.
    """
    AuthConfigManager.purge_access_token()
