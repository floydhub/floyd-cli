import click
import webbrowser

import floyd
from floyd.client.auth import AuthClient
from floyd.manager.auth_config import AuthConfigManager
from floyd.model.access_token import AccessToken
from floyd.log import logger as floyd_logger


@click.command()
@click.option('--token', is_flag=True, default=False, help='Just enter token')
def login(token):
    """
    Log into Floyd via Auth0.
    """
    if not token:
        cli_info_url = "{}/welcome".format(floyd.floyd_web_host)
        click.confirm('Authentication token page will now open in your browser. Continue?', abort=True, default=True)

        webbrowser.open(cli_info_url)

    floyd_logger.info("Please copy and paste the token from the welcome page.")
    access_code = click.prompt('This is an invisible field. Paste token and press ENTER', type=str, hide_input=True)

    if not access_code:
        floyd_logger.info("Empty token received. Make sure your shell is handling the token appropriately.")
        floyd_logger.info("See FAQ for help: http://docs.floydhub.com/faq/")
        return

    access_code = access_code.strip(" ")
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
