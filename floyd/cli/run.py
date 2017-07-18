from __future__ import print_function
import click
from tabulate import tabulate
from time import sleep
import webbrowser
import sys

from floyd.constants import DEFAULT_ENV
from floyd.client.data import DataClient
from floyd.cli.utils import get_mode_parameter, wait_for_url, get_data_name
from floyd.client.experiment import ExperimentClient
from floyd.client.module import ModuleClient
from floyd.client.env import EnvClient
from floyd.manager.auth_config import AuthConfigManager
from floyd.manager.experiment_config import ExperimentConfigManager
from floyd.constants import CPU_INSTANCE_TYPE, GPU_INSTANCE_TYPE
from floyd.model.module import Module
from floyd.model.experiment import ExperimentRequest
from floyd.log import logger as floyd_logger


@click.command()
@click.option('--gpu/--cpu', default=False, help='Run on a gpu instance')
@click.option('--data', multiple=True, help='Data source id to use')
@click.option('--mode',
              help='Different floyd modes',
              default='job',
              type=click.Choice(['job', 'jupyter', 'serve']))
@click.option('--open/--no-open',
              help='Automatically open the notebook url',
              default=True)
@click.option('--env',
              help='Environment type to use',
              default=DEFAULT_ENV)
@click.option('--message', '-m',
              help='Experiment commit message')
@click.option('--tensorboard/--no-tensorboard',
              help='Run tensorboard in the experiment environment')
@click.argument('command', nargs=-1)
@click.pass_context
def run(ctx, gpu, env, message, data, mode, open, tensorboard, command):
    """
    Run a command on Floyd. Floyd will upload contents of the
    current directory and run your command remotely.
    This command will generate a run id for reference.
    """
    command_str = ' '.join(command)
    experiment_config = ExperimentConfigManager.get_config()
    access_token = AuthConfigManager.get_access_token()
    experiment_name = "{}/{}".format(access_token.username,
                                     experiment_config.name)

    # Get the actual command entered in the command line
    full_command = get_command_line(gpu, env, message, data, mode, open, tensorboard, command)

    # Create module
    if len(data) > 5:
        floyd_logger.error(
            "Cannot attach more than 5 datasets to an experiment")
        return

    # Get the data entity from the server to:
    # 1. Confirm that the data id or uri exists and has the right permissions
    # 2. If uri is used, get the id of the dataset
    data_ids = []
    for data_name_or_id in data:
        path = None
        if ':' in data_name_or_id:
            data_name_or_id, path = data_name_or_id.split(':')
        data_obj = DataClient().get(data_name_or_id)
        if not data_obj:
            floyd_logger.error("Data not found for name or id: {}".format(data_name_or_id))
            return
        data_ids.append("{}:{}".format(data_obj.id, path) if path else data_obj.id)

    default_name = 'input' if len(data_ids) <= 1 else None
    module_inputs = [{'name': get_data_name(data_str, default_name),
                      'type': 'dir'} for data_str in data_ids]

    if gpu:
        arch = 'gpu'
        instance_type = GPU_INSTANCE_TYPE
    else:
        arch = 'cpu'
        instance_type = CPU_INSTANCE_TYPE

    env_map = EnvClient().get_all()
    envs = env_map.get(arch)
    if envs:
        if env not in envs:
            floyd_logger.error(
                "{} is not in the list of supported environments: {}".format(
                    env, ', '.join(envs.keys())))
            return
    else:
        floyd_logger.error("{} is not a supported architecture".format(arch))
        return

    module = Module(name=experiment_name,
                    description=message or '',
                    command=command_str,
                    mode=get_mode_parameter(mode),
                    enable_tensorboard=tensorboard,
                    family_id=experiment_config.family_id,
                    inputs=module_inputs,
                    env=env,
                    arch=arch)

    from floyd.exceptions import BadRequestException
    try:
        module_id = ModuleClient().create(module)
    except BadRequestException as e:
        if 'Project not found, ID' in e.message:
            floyd_logger.error(
                'ERROR: Please run "floyd init PROJECT_NAME" before scheduling a job.')
        else:
            floyd_logger.error('ERROR: %s', e.message)
        sys.exit(1)
    floyd_logger.debug("Created module with id : {}".format(module_id))

    # Create experiment request
    experiment_request = ExperimentRequest(name=experiment_name,
                                           description=message,
                                           full_command=full_command,
                                           module_id=module_id,
                                           data_ids=data_ids,
                                           family_id=experiment_config.family_id,
                                           instance_type=instance_type)
    expt_info = ExperimentClient().create(experiment_request)
    floyd_logger.debug("Created experiment : {}".format(expt_info['id']))

    table_output = [["RUN ID", "NAME"],
                    [expt_info['id'], expt_info['name']]]
    floyd_logger.info(tabulate(table_output, headers="firstrow"))
    floyd_logger.info("")

    if mode in ['jupyter', 'serve']:
        while True:
            # Wait for the experiment / task instances to become available
            try:
                experiment = ExperimentClient().get(expt_info['id'])
                if experiment.task_instances:
                    break
            except Exception:
                floyd_logger.debug("Experiment not available yet: {}".format(expt_info['id']))

            floyd_logger.debug("Experiment not available yet: {}".format(expt_info['id']))
            sleep(3)
            continue

        # Print the path to jupyter notebook
        if mode == 'jupyter':
            jupyter_url = experiment.service_url
            print("Setting up your instance and waiting for Jupyter notebook to become available ...", end='')
            if wait_for_url(jupyter_url, sleep_duration_seconds=2, iterations=900):
                floyd_logger.info("\nPath to jupyter notebook: {}".format(jupyter_url))
                if open:
                    webbrowser.open(jupyter_url)
            else:
                floyd_logger.info("\nPath to jupyter notebook: {}".format(jupyter_url))
                floyd_logger.info("Notebook is still loading. View logs to track progress")
                floyd_logger.info("   floyd logs {}".format(expt_info['name']))

        # Print the path to serving endpoint
        if mode == 'serve':
            floyd_logger.info("Path to service endpoint: {}".format(experiment.service_url))

        if experiment.timeout_seconds < 4 * 60 * 60:
            floyd_logger.info("\nYour job timeout is currently set to {} seconds".format(experiment.timeout_seconds))
            floyd_logger.info("This is because you are in a trial account. Paid users will have longer timeouts. "
                              "See https://www.floydhub.com/pricing for details")

    else:
        floyd_logger.info("To view logs enter:")
        floyd_logger.info("   floyd logs {}".format(expt_info['name']))


def get_command_line(gpu, env, message, data, mode, open, tensorboard, command):
    """
    Return a string representing the full floyd command entered in the command line
    """
    floyd_command = "floyd run"
    if not env == DEFAULT_ENV:
        floyd_command = floyd_command + " --env {}".format(env)
    if message:
        floyd_command = floyd_command + " --message \"{}\"".format(message)
    if data:
        for data_item in data:
            floyd_command = floyd_command + " --data {}".format(data_item)
    if not mode == "job":
        floyd_command = floyd_command + " --mode {}".format(mode)
    if gpu:
        floyd_command = floyd_command + " --gpu"
    if not open:
        floyd_command = floyd_command + " --no-open"
    if tensorboard:
        floyd_command = floyd_command + " --tensorboard"
    if command:
        floyd_command = floyd_command + " \"{}\"".format(' '.join(command))
    return floyd_command
