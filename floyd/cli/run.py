import click
from tabulate import tabulate

from floyd.client.experiment import ExperimentClient
from floyd.client.module import ModuleClient
from floyd.config import AuthConfigManager, ExperimentConfigManager
from floyd.constants import (CPU_INSTANCE_TYPE, GPU_INSTANCE_TYPE,
                             TENSORFLOW_CPU_DOCKER_IMAGE, TENSORFLOW_GPU_DOCKER_IMAGE)
from floyd.model.module import Module
from floyd.model.experiment import ExperimentRequest
from floyd.log import logger as floyd_logger


@click.command()
@click.option('--gpu/--cpu', default=False, help='Run on a gpu instance')
@click.argument('command', nargs=-1)
def run(gpu, command):
    """
    Run a command on Floyd. Floyd will upload contents of the
    current directory and run your command remotely.
    This command will generate a run id for reference.
    """
    command_str = ' '.join(command)
    experiment_config = ExperimentConfigManager.get_config()
    access_token = AuthConfigManager.get_access_token()
    version = experiment_config.version

    # Create module
    module = Module(name=experiment_config.name,
                    description=experiment_config.name,
                    command=command_str,
                    family_id=experiment_config.family_id,
                    default_container=TENSORFLOW_GPU_DOCKER_IMAGE if gpu else TENSORFLOW_CPU_DOCKER_IMAGE,
                    version=version)
    module_id = ModuleClient().create(module)
    floyd_logger.debug("Created module with id : {}".format(module_id))

    # Create experiment request
    experiment_name = "{}/{}:{}".format(access_token.username,
                                        experiment_config.name,
                                        version)
    instance_type = GPU_INSTANCE_TYPE if gpu else CPU_INSTANCE_TYPE
    experiment_request = ExperimentRequest(name=experiment_name,
                                           description=version,
                                           module_id=module_id,
                                           predecessor=experiment_config.experiment_predecessor,
                                           family_id=experiment_config.family_id,
                                           version=version,
                                           instance_type=instance_type)
    experiment_id = ExperimentClient().create(experiment_request)
    floyd_logger.debug("Created experiment : {}".format(experiment_id))

    # Update expt config including predecessor
    experiment_config.increment_version()
    experiment_config.set_module_predecessor(module_id)
    experiment_config.set_experiment_predecessor(experiment_id)
    ExperimentConfigManager.set_config(experiment_config)

    table_output = [["RUN ID", "NAME", "VERSION"],
                    [experiment_id, experiment_name, version]]
    floyd_logger.info(tabulate(table_output, headers="firstrow"))
