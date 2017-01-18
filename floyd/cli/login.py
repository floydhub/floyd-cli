import click

from floyd.client.login import LoginClient
from floyd.config import FloydConfigManager
from floyd.model.credentials import Credentials
from floyd.logging import logger as floyd_logger


@click.command()
@click.option('--username', required=True, help='Floyd username')
@click.option('--password', prompt=True, required=True, hide_input=True, help='Floyd password')
def login(username, password):
    credentials = Credentials(username, password)
    access_token = LoginClient().login(credentials)
    config_manager = FloydConfigManager()
    config_manager.set_access_token(access_token)
    floyd_logger.info("Login Successful")
