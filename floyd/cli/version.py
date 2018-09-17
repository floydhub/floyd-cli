import click

from floyd.log import logger as floyd_logger


PROJECT_NAME = "floyd-cli"


def pip_upgrade():
    import sys
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', "--upgrade", PROJECT_NAME])
    floyd_logger.info("Upgrade completed.")


def conda_upgrade():
    floyd_logger.info("To upgrade please run:\nconda install -y -c floydhub -c conda-forge floyd-cli")


@click.command()
def version():
    """
    View the current version of the CLI.
    """
    import pkg_resources
    version = pkg_resources.require(PROJECT_NAME)[0].version
    floyd_logger.info(version)


def auto_upgrade():
    try:
        from floyd.cli.utils import is_conda_env
        if is_conda_env():
            conda_upgrade()
        else:
            pip_upgrade()
    except Exception as e:
        floyd_logger.error(e)


@click.command()
def upgrade():
    """
    Upgrade CLI to the latest version.
    """
    auto_upgrade()
