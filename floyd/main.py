import click
import sys
from distutils.version import LooseVersion

import floyd
from floyd.cli.utils import get_cli_version, is_conda_env
from floyd.cli.auth import login, logout
from floyd.cli.data import data
from floyd.cli.experiment import clone, delete, info, init, logs, output, status, stop
from floyd.cli.run import run, restart
from floyd.cli.version import upgrade, version, auto_upgrade
from floyd.client.version import VersionClient
from floyd.log import configure_logger


@click.group()
@click.option('-h', '--host', default='https://www.floydhub.com', help='Floyd server endpoint')
@click.option('-v', '--verbose', count=True, help='Turn on debug logging')
def cli(host, verbose):
    """
    Floyd CLI interacts with FloydHub server and executes your commands.
    Detailed help is available at https://docs.floydhub.com/commands/.
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
    should_exit = False
    server_version = VersionClient().get_cli_version()
    current_version = get_cli_version()

    if LooseVersion(current_version) < LooseVersion(server_version.min_version):
        print("\nYour version of CLI (%s) is no longer compatible with server." % current_version)
        should_exit = True
    elif LooseVersion(current_version) < LooseVersion(server_version.latest_version):
        print("\nNew version of CLI (%s) is now available." % server_version.latest_version)
    else:
        return

    # new version is ready
    if should_exit and click.confirm('\nDo you want to upgrade to version %s now?' % server_version.latest_version):
        auto_upgrade()
        sys.exit(0)
    else:
        msg_parts = []
        msg_parts.append("\nTo manually upgrade run:")
        msg_parts.append("    pip install -U floyd-cli")
        if is_conda_env():
            msg_parts.append("Or if you prefer to use conda:")
            msg_parts.append("    conda install -y -c conda-forge -c floydhub floyd-cli")
        print("\n".join(msg_parts))
        print("")

    if should_exit:
        sys.exit(0)


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
