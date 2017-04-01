import pip
import pkg_resources
import click

from floyd.log import logger as floyd_logger


PROJECT_NAME = "floyd-cli"


@click.command()
def version():
    """
    Prints the current version of the CLI
    """
    version = pkg_resources.require(PROJECT_NAME)[0].version
    floyd_logger.info(version)


@click.command()
def upgrade():
    """
    Upgrade floyd command line
    """
    try:
        pip.main(["install", "--upgrade", PROJECT_NAME])
    except Exception as e:
        floyd_logger.error(e)
