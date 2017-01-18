import click

from floyd.client.ps import PsClient
from floyd.logging import logger as floyd_logger


@click.command()
@click.argument('id', nargs=1)
def ps(id):
    if id:
        experiment = PsClient().get(id)
        floyd_logger.info(experiment.to_dict())
    else:
        experiments = PsClient().get_all()
        for experiment in experiments:
            floyd_logger.info(experiment.to_dict())
