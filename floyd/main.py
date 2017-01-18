import click

import floyd
from floyd.cli.auth import login, logout
from floyd.cli.experiment import logs, output, ps, stop


@click.group()
@click.option('--host', default='https://beta.floydhub.com', help='Floyd server endpoint')
def cli(host):
    floyd.floyd_host = host


cli.add_command(login)
cli.add_command(logout)
cli.add_command(logs)
cli.add_command(output)
cli.add_command(ps)
cli.add_command(stop)
