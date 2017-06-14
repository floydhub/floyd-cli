import click
from distutils.version import LooseVersion
import pkg_resources

import floyd
from floyd.cli.auth import login, logout
from floyd.cli.data import data
from floyd.cli.experiment import delete, info, init, logs, output, status, stop
from floyd.cli.run import run
from floyd.cli.version import upgrade, version
from floyd.client.version import VersionClient
from floyd.exceptions import FloydException
from floyd.log import configure_logger


@click.group()
@click.option('-h', '--host', default='https://www.floydhub.com', help='Floyd server endpoint')
@click.option('-v', '--verbose', count=True, help='Turn on debug logging')
def cli(host, verbose):
    """
    Floyd CLI interacts with Floyd server and executes your commands.
    More help is available under each command listed below.
    """
    floyd.floyd_host = host
    configure_logger(verbose)
    check_cli_version()


def check_cli_version():
    """
    Check if the current cli version satisfies the server requirements
    """
    server_version = VersionClient().get_cli_version()
    current_version = pkg_resources.require("floyd-cli")[0].version
    if LooseVersion(current_version) < LooseVersion(server_version.min_version):
        raise FloydException("""
Your version of CLI ({}) is no longer compatible with server. Run:
    pip install -U floyd-cli
to upgrade to the latest version ({})
            """.format(current_version, server_version.latest_version))
    if LooseVersion(current_version) < LooseVersion(server_version.latest_version):
        print("""
New version of CLI ({}) is now available. To upgrade run:
    pip install -U floyd-cli
            """.format(server_version.latest_version))


def add_commands(cli):
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
    cli.add_command(run)
    cli.add_command(upgrade)
    cli.add_command(version)

add_commands(cli)
