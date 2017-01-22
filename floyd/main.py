import click

import floyd
from floyd.log import configure_logger
from floyd.cli.auth import demo, login, logout
from floyd.cli.experiment import init, logs, output, status, stop
from floyd.cli.run import run


@click.group()
@click.option('-h', '--host', default='https://beta.floydhub.com', help='Floyd server endpoint')
@click.option('-v', '--verbose', count=True, help='Turn on debug logging')
def cli(host, verbose):
    """
    Floyd CLI interacts with Floyd server and executes your commands.
    More help is available under each command listed below.
    """
    floyd.floyd_host = host
    configure_logger(verbose)


cli.add_command(demo)
cli.add_command(init)
cli.add_command(login)
cli.add_command(logout)
cli.add_command(logs)
cli.add_command(output)
cli.add_command(status)
cli.add_command(stop)
cli.add_command(run)
