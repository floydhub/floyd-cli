import click

from floyd.client.auth import AuthClient
from floyd.config import AuthConfigManager, generate_uuid
from floyd.constants import FIRST_STEPS_DOC
from floyd.model.credentials import Credentials, SignupRequest
from floyd.log import logger as floyd_logger


@click.command()
@click.option('--username', prompt=True, required=True, help='Floyd username')
@click.option('--password', prompt=True, required=True, hide_input=True, help='Floyd password')
def login(username, password):
    """
    Log into Floyd using your credentials.
    Signup before first login.
    """
    credentials = Credentials(username, password)
    access_token = AuthClient().login(credentials)
    AuthConfigManager.set_access_token(access_token)
    floyd_logger.info("Login Successful")


@click.command()
def logout():
    """
    Logout of Floyd.
    """
    AuthConfigManager.purge_access_token()
    if AuthClient().logout():
        floyd_logger.info("Logout Successful")


@click.command()
def demo():
    """
    Try Floyd with a demo account.
    All functionalities of Floyd can be tested in this mode but the time and project
    limits are much smaller with a demo account.
    """
    if AuthConfigManager.get_access_token():
        floyd_logger.info("User already signed in")
        floyd_logger.info(FIRST_STEPS_DOC)
        return

    demo_username = "demo_{}".format(generate_uuid())
    demo_password = generate_uuid()
    signup_request = SignupRequest(username=demo_username,
                                   password=demo_password,
                                   password_confirmation=demo_password,
                                   email="{}@gmail.com".format(demo_username),
                                   invite_code="demo")
    access_token = AuthClient().signup(signup_request)
    AuthConfigManager.set_access_token(access_token)
    floyd_logger.info("Demo mode is ON")
    floyd_logger.info(FIRST_STEPS_DOC)
