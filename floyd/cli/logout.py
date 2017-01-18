import click

from floyd.config import FloydConfigManager
from floyd.logging import logger as floyd_logger


@click.command()
def logout():
    FloydConfigManager.purge_access_token()
    floyd_logger.info("Logout Successful")
