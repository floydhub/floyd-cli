import click
from tabulate import tabulate
from time import sleep

from floyd.constants import DOCKER_IMAGES
from floyd.cli.utils import (get_task_url, get_docker_image, get_module_task_instance_id,
                             get_mode_parameter, wait_for_url)
from floyd.client.experiment import ExperimentClient
from floyd.client.module import ModuleClient
from floyd.manager.auth_config import AuthConfigManager
from floyd.manager.experiment_config import ExperimentConfigManager
from floyd.constants import CPU_INSTANCE_TYPE, GPU_INSTANCE_TYPE
from floyd.model.module import Module
from floyd.model.experiment import ExperimentRequest
from floyd.log import logger as floyd_logger


@click.command()
@click.option('--gpu/--cpu', default=False, help='Run on a gpu instance')
@click.option('--data', help='Data source id to use')
@click.option('--mode',
              help='Different floyd modes',
              default='job',
              type=click.Choice(['job', 'jupyter', 'serve']))
@click.option('--env',
              help='Environment type to use',
              default='keras',
              type=click.Choice(sorted(DOCKER_IMAGES["cpu"].keys())))
@click.argument('command', nargs=-1)
@click.pass_context
def run(ctx, gpu, env, data, mode, command):
    """
    Run a command on Floyd. Floyd will upload contents of the
    current directory and run your command remotely.
    This command will generate a run id for reference.
    """
    command_str = ' '.join(command)
    experiment_config = ExperimentConfigManager.get_config()
    access_token = AuthConfigManager.get_access_token()
    version = experiment_config.version
    experiment_name = "{}/{}:{}".format(access_token.username,
                                        experiment_config.name,
                                        version)

    # Create module
    module = Module(name=experiment_name,
                    description=version,
                    command=command_str,
                    mode=get_mode_parameter(mode),
                    family_id=experiment_config.family_id,
                    default_container=get_docker_image(env, gpu),
                    version=version)
    module_id = ModuleClient().create(module)
    floyd_logger.debug("Created module with id : {}".format(module_id))

    # Create experiment request
    instance_type = GPU_INSTANCE_TYPE if gpu else CPU_INSTANCE_TYPE
    experiment_request = ExperimentRequest(name=experiment_name,
                                           description=version,
                                           module_id=module_id,
                                           data_id=data,
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
    floyd_logger.info("")

    if mode != 'default':
        while True:
            # Wait for the experiment to become available
            try:
                experiment = ExperimentClient().get(experiment_id)
                break
            except Exception:
                floyd_logger.debug("Experiment not available yet: {}".format(experiment_id))
                sleep(1)
                continue

        # Print the path to jupyter notebook
        if mode == 'jupyter':
            jupyter_url = get_task_url(get_module_task_instance_id(experiment.task_instances))
            floyd_logger.info("Waiting for Jupyter notebook to become available ...")
            if wait_for_url(jupyter_url):
                floyd_logger.info("\nPath to jupyter notebook: {}".format(jupyter_url))
            else:
                floyd_logger.info("Problem starting the notebook. View logs for more information")

        # Print the path to serving endpoint
        if mode == 'serve':
            floyd_logger.info("Path to service endpoint: {}".format(
                get_task_url(get_module_task_instance_id(experiment.task_instances))))

    floyd_logger.info("""
To view logs enter:
    floyd logs {}
        """.format(experiment_id))
