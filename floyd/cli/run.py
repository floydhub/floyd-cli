import click

from floyd.client.experiment import ExperimentClient
from floyd.client.module import ModuleClient
from floyd.config import AuthConfigManager, ExperimentConfigManager
from floyd.model.module import Module
from floyd.model.experiment import ExperimentRequest
from floyd.logging import logger as floyd_logger


@click.command()
@click.argument('command', nargs=-1)
def run(command):
    command_str = ' '.join(command)
    experiment_config = ExperimentConfigManager.get_config()
    access_token = AuthConfigManager.get_access_token()
    version = experiment_config.version

    # Create module
    module = Module(name=experiment_config.name,
                    description=experiment_config.name,
                    command=command_str,
                    family_id=experiment_config.family_id,
                    version=version)
    module_id = ModuleClient().create(module)
    floyd_logger.debug("Created module with id : {}".format(module_id))

    # Create experiment request
    experiment_name = "{}/{}:{}".format(access_token.username,
                                        experiment_config.name,
                                        version)
    experiment_request = ExperimentRequest(name=experiment_name,
                                           description=version,
                                           module_id=module_id,
                                           predecessor=experiment_config.experiment_predecessor,
                                           family_id=experiment_config.family_id,
                                           version=version)
    experiment_id = ExperimentClient().create(experiment_request)
    floyd_logger.debug("Created experiment : {}".format(experiment_id))

    experiment_config.increment_version()
    experiment_config.set_module_predecessor(module_id)
    experiment_config.set_experiment_predecessor(experiment_id)
    ExperimentConfigManager.set_config(experiment_config)
    floyd_logger.info("Run created. Id: {}, version: {}".format(experiment_id, version))
