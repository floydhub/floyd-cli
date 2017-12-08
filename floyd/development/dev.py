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
    floyd.floyd_host = floyd.floyd_web_host = "https://dev.floydhub.com"
    floyd.tus_server_endpoint = "https://upload-v2-dev.floydhub.com/api/v1/upload/"
    configure_logger(verbose)
    check_cli_version()


add_commands(cli)
