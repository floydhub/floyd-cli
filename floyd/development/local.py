import click

import floyd
from floyd.log import configure_logger
from floyd.main import check_cli_version, add_commands


@click.group()
@click.option('-v', '--verbose', count=True, help='Turn on debug logging')
def cli(verbose):
    """
    Floyd CLI interacts with FloydHub server and executes your commands.
    More help is available under each command listed below.
    """
    floyd.floyd_host = "http://localhost:8080"
    floyd.floyd_web_host = "http://localhost:3000"
    floyd.tus_server_endpoint = "http://localhost:1080"
    configure_logger(verbose)
    check_cli_version()


add_commands(cli)
