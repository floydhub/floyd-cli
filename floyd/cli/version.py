import pip
import pkg_resources
import click

from floyd.cli.utils import is_conda_env
from floyd.log import logger as floyd_logger


PROJECT_NAME = "floyd-cli"


def pip_upgrade():
    pip.main(["install", "--upgrade", PROJECT_NAME])


def conda_upgrade():
    floyd_logger.info("To upgrade please run:\nconda install -y -c floydhub -c conda-forge floyd-cli")


@click.command()
def version():
    """
    Prints the current version of the CLI
    """
    version = pkg_resources.require(PROJECT_NAME)[0].version
    floyd_logger.info(version)


def auto_upgrade():
    try:
        if is_conda_env():
            conda_upgrade()
        else:
            pip_upgrade()
    except Exception as e:
        floyd_logger.error(e)


@click.command()
def upgrade():
    """
    Upgrade floyd command line
    """
    auto_upgrade()
