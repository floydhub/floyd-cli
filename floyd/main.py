import click

import floyd
from floyd.cli.login import login
from floyd.cli.logout import logout
from floyd.cli.ps import ps


@click.group()
@click.option('--host', default='https://beta.floydhub.com', help='Floyd server endpoint')
def cli(host):
    floyd.floyd_host = host


cli.add_command(login)
cli.add_command(logout)
cli.add_command(ps)
