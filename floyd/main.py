import click
import sys
from distutils.version import LooseVersion

import floyd
from floyd.cli.utils import get_cli_version
from floyd.cli.auth import login, logout
from floyd.cli.data import data
from floyd.cli.experiment import clone, delete, info, init, logs, output, status, stop
from floyd.cli.run import run, restart
from floyd.cli.version import upgrade, version
from floyd.client.version import VersionClient
from floyd.log import configure_logger


@click.group()
@click.option('-h', '--host', default='https://www.floydhub.com', help='Floyd server endpoint')
@click.option('-v', '--verbose', count=True, help='Turn on debug logging')
def cli(host, verbose):
    """
    Floyd CLI interacts with FloydHub server and executes your commands.
    More help is available under each command listed below.
    """
    import raven
    raven.Client(
        dsn='https://d8669005bd2b4b1ba6387ec57e1ce660:1d25ce33fcdb4864b9fd4f0c97689a98@sentry.io/226940',
        release=get_cli_version(),
        environment='prod',
        processors=('raven.processors.SanitizePasswordsProcessor',))

    floyd.floyd_host = host
    configure_logger(verbose)
    check_cli_version()


def check_cli_version():
    """
    Check if the current cli version satisfies the server requirements
    """
    server_version = VersionClient().get_cli_version()
    current_version = get_cli_version()
    if LooseVersion(current_version) < LooseVersion(server_version.min_version):
        print("""
Your version of CLI (%s) is no longer compatible with server.""" % current_version)
        if click.confirm('Do you want to upgrade to version %s now?' % server_version.latest_version):
            from floyd.cli.version import pip_upgrade
            pip_upgrade()
            sys.exit(0)
        else:
            print("""Your can manually run:
    pip install -U floyd-cli
to upgrade to the latest version (%s))""" % server_version.latest_version)
            sys.exit(0)
    elif LooseVersion(current_version) < LooseVersion(server_version.latest_version):
        print("""
New version of CLI (%s) is now available. To upgrade run:
    pip install -U floyd-cli
            """ % server_version.latest_version)


def add_commands(cli):
    cli.add_command(clone)
    cli.add_command(data)
    cli.add_command(delete)
    cli.add_command(info)
    cli.add_command(init)
    cli.add_command(login)
    cli.add_command(logout)
    cli.add_command(logs)
    cli.add_command(output)
    cli.add_command(status)
    cli.add_command(stop)
    cli.add_command(restart)
    cli.add_command(run)
    cli.add_command(upgrade)
    cli.add_command(version)


add_commands(cli)
