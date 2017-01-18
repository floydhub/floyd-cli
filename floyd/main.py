import click

import floyd
from floyd.cli.login import login
from floyd.cli.logout import logout


@click.group()
@click.option('--host', default='beta.floydhub.com', help='Floyd server endpoint')
def cli(host):
    floyd.floyd_host = host


cli.add_command(login)
cli.add_command(logout)
