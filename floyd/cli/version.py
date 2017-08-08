import pip
import pkg_resources
import click

from floyd.log import logger as floyd_logger


PROJECT_NAME = "floyd-cli"


def pip_upgrade():
    pip.main(["install", "--upgrade", PROJECT_NAME])


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
        pip_upgrade()
    except Exception as e:
        floyd_logger.error(e)
