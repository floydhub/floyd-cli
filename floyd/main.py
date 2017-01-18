import click
import logging

import floyd
from floyd.cli.auth import login, logout
from floyd.cli.experiment import init, logs, output, ps, stop


@click.group()
@click.option('-h', '--host', default='https://beta.floydhub.com', help='Floyd server endpoint')
@click.option('-v', '--verbose', count=True, help='Turn on debug logging')
def cli(host, verbose):
    floyd.floyd_host = host
    configure_logger(verbose)


def configure_logger(verbose):
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(format='%(message)s', level=log_level)


cli.add_command(init)
cli.add_command(login)
cli.add_command(logout)
cli.add_command(logs)
cli.add_command(output)
cli.add_command(ps)
cli.add_command(stop)
