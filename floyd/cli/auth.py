import click
import webbrowser

import floyd
from floyd.client.auth import AuthClient
from floyd.manager.auth_config import AuthConfigManager
from floyd.model.access_token import AccessToken
from floyd.model.credentials import Credentials
from floyd.log import logger as floyd_logger


@click.command()
@click.option('--token', is_flag=True, default=False, help='Just enter token')
@click.option('--username', '-u', help='FloydHub username')
@click.option('--password', '-p', help='FloydHub password')
def login(token, username, password):
    """
    Log into Floyd via Auth0.
    """
    if username:
        # Use username / password login
        if not password:
            floyd_logger.info("Missing --password field")
            return

        login_credentials = Credentials(username=username,
                                        password=password)
        access_code = AuthClient().login(login_credentials)
        if not access_code:
            floyd_logger.info("Failed to login")
            return

    else:
        # Fallback to the access token from the browser login
        if not token:
            cli_info_url = "{}/settings/security".format(floyd.floyd_web_host)
            click.confirm('Authentication token page will now open in your browser. Continue?',
                          abort=True,
                          default=True)
            webbrowser.open(cli_info_url)

        floyd_logger.info("Please copy and paste the authentication token.")
        access_code = click.prompt('This is an invisible field. Paste token and press ENTER', type=str, hide_input=True)

        access_code = access_code.strip()

        if not access_code:
            floyd_logger.info("Empty token received. Make sure your shell is handling the token appropriately.")
            floyd_logger.info("See docs for help: http://docs.floydhub.com/faqs/authentication/")
            return

        access_code = access_code.strip(" ")

    user = AuthClient().get_user(access_code)
    access_token = AccessToken(username=user.username,
                               token=access_code)
    AuthConfigManager.set_access_token(access_token)
    floyd_logger.info("Login Successful as %s", user.username)


@click.command()
def logout():
    """
    Logout of Floyd.
    """
    AuthConfigManager.purge_access_token()
