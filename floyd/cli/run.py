import click

from floyd.client.module import ModuleClient
from floyd.config import ExperimentConfigManager
from floyd.model.module import Module
from floyd.logging import logger as floyd_logger


@click.command()
@click.argument('command', nargs=-1)
def run(command):
    command_str = ' '.join(command)
    experiment_config = ExperimentConfigManager.get_config()
    experiment_name = "{}-{}".format(experiment_config.name,
                                     experiment_config.version)

    module = Module(name=experiment_name,
                    description=experiment_name,
                    command=command_str)
    module_id = ModuleClient().create(module)
    floyd_logger.debug("Created module with id : {}".format(module_id))

    experiment_config.increment_version()
    ExperimentConfigManager.set_config(experiment_config)
