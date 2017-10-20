from __future__ import print_function
import click
from tabulate import tabulate
from time import sleep
import webbrowser
import sys
try:
    from pipes import quote as shell_quote
except:
    from shlex import quote as shell_quote

import floyd
from floyd.constants import DEFAULT_ENV, INSTANCE_NAME_MAP
from floyd.client.data import DataClient
from floyd.client.project import ProjectClient
from floyd.cli.utils import (
    get_mode_parameter, get_data_name, normalize_job_name
)
from floyd.client.experiment import ExperimentClient
from floyd.client.module import ModuleClient
from floyd.client.env import EnvClient
from floyd.manager.auth_config import AuthConfigManager
from floyd.manager.experiment_config import ExperimentConfigManager
from floyd.constants import (
    G1P_INSTANCE_TYPE, C1P_INSTANCE_TYPE, C1_INSTANCE_TYPE, G1_INSTANCE_TYPE,
    INSTANCE_ARCH_MAP
)
from floyd.model.module import Module
from floyd.model.experiment import ExperimentRequest
from floyd.log import logger as floyd_logger
from floyd.exceptions import BadRequestException


def process_data_ids(data):
    if len(data) > 5:
        floyd_logger.error(
            "Cannot attach more than 5 datasets to a job")
        return False, None

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
            return False, None
        if path:
            data_ids.append("%s:%s" % (data_obj.id, path))
        else:
            data_ids.append(data_obj.id)
    return True, data_ids


def validate_env(env, instance_type):
    arch = INSTANCE_ARCH_MAP[instance_type]
    env_map = EnvClient().get_all()
    envs = env_map.get(arch)
    if envs:
        if env not in envs:
            floyd_logger.error(
                "{} is not in the list of supported environments:\n{}".format(
                    env, tabulate([[env_name] for env_name in envs.keys()])))
            return False
    else:
        floyd_logger.error("invalid instance type")
        return False

    return True


def show_new_job_info(expt_client, job_name, expt_info, mode, open_notebook=True):
    if mode in ['jupyter', 'serve']:
        while True:
            # Wait for the experiment / task instances to become available
            try:
                experiment = expt_client.get(expt_info['id'])
                if experiment.task_instances:
                    break
            except Exception:
                floyd_logger.debug("Job not available yet: %s", expt_info['id'])

            floyd_logger.debug("Job not available yet: %s", expt_info['id'])
            sleep(3)
            continue

        # Print the path to jupyter notebook
        if mode == 'jupyter':
            if not experiment.service_url:
                floyd_logger.error("Jupyter not available, please check job state and log for error.")
                sys.exit(1)

            jupyter_url = '%s/%s' % (floyd.floyd_web_host, job_name)
            floyd_logger.info("\nPath to jupyter notebook: %s", jupyter_url)
            if open_notebook:
                webbrowser.open(jupyter_url)

        # Print the path to serving endpoint
        if mode == 'serve':
            floyd_logger.info("Path to service endpoint: %s", experiment.service_url)

        if experiment.timeout_seconds < 24 * 60 * 60:
            floyd_logger.info("\nYour job timeout is currently set to %s seconds",
                              experiment.timeout_seconds)
            floyd_logger.info("This is because you are in the free plan. Paid users will have longer timeouts. "
                              "See https://www.floydhub.com/pricing for details")

    else:
        floyd_logger.info("To view logs enter:")
        floyd_logger.info("   floyd logs %s", job_name)


@click.command()
@click.option('--gpu/--cpu', default=False, help='Run on a GPU instance')
@click.option('--data', multiple=True, help='Data source id to use')
@click.option('--mode',
              help='Different floyd modes',
              default='job',
              type=click.Choice(['job', 'jupyter', 'serve']))
@click.option('--open/--no-open', 'open_notebook',
              help='Automatically open the notebook url',
              default=True)
@click.option('--env',
              help='Environment type to use',
              default=DEFAULT_ENV)
@click.option('--message', '-m',
              help='Job commit message')
@click.option('--tensorboard/--no-tensorboard',
              help='Run tensorboard in the job environment')
@click.option('--gpu+', 'gpup', is_flag=True, help='Run in a GPU+ instance')
@click.option('--cpu+', 'cpup', is_flag=True, help='Run in a CPU+ instance')
@click.argument('command', nargs=-1)
@click.pass_context
def run(ctx, gpu, env, message, data, mode, open_notebook, tensorboard, gpup, cpup, command):
    """
    Run a command on Floyd. Floyd will upload contents of the
    current directory and run your command remotely.
    This command will generate a run id for reference.
    """
    experiment_config = ExperimentConfigManager.get_config()
    if not ProjectClient().exists(experiment_config.family_id):
        floyd_logger.error('Invalid project id, please run '
                           '"floyd init PROJECT_NAME" before scheduling a job.')
        sys.exit(1)

    access_token = AuthConfigManager.get_access_token()
    experiment_name = "{}/{}".format(access_token.username,
                                     experiment_config.name)

    success, data_ids = process_data_ids(data)
    if not success:
        sys.exit(2)

    # Create module
    default_name = 'input' if len(data_ids) <= 1 else None
    module_inputs = [{'name': get_data_name(data_str, default_name),
                      'type': 'dir'} for data_str in data_ids]

    if gpup:
        instance_type = G1P_INSTANCE_TYPE
    elif cpup:
        instance_type = C1P_INSTANCE_TYPE
    elif gpu:
        instance_type = G1_INSTANCE_TYPE
    else:
        instance_type = C1_INSTANCE_TYPE

    if not validate_env(env, instance_type):
        sys.exit(3)

    command_str = ' '.join(command)
    if command_str and mode in ('jupyter', 'serve'):
        floyd_logger.error('Command argument "%s" cannot be used with mode: %s.\nSee http://docs.floydhub.com/guides/run_a_job/#mode for more information about run modes.', command_str, mode)
        sys.exit(3)

    module = Module(name=experiment_name,
                    description=message or '',
                    command=command_str,
                    mode=get_mode_parameter(mode),
                    enable_tensorboard=tensorboard,
                    family_id=experiment_config.family_id,
                    inputs=module_inputs,
                    env=env,
                    arch=INSTANCE_ARCH_MAP[instance_type])

    try:
        module_id = ModuleClient().create(module)
    except BadRequestException as e:
        if 'Project not found, ID' in e.message:
            floyd_logger.error(
                'ERROR: Please run "floyd init PROJECT_NAME" before scheduling a job.')
        else:
            floyd_logger.error('ERROR: %s', e.message)
        sys.exit(4)
    floyd_logger.debug("Created module with id : %s", module_id)

    # Create experiment request
    # Get the actual command entered in the command line
    full_command = get_command_line(instance_type, env, message, data, mode, open_notebook, tensorboard, command_str)
    experiment_request = ExperimentRequest(name=experiment_name,
                                           description=message,
                                           full_command=full_command,
                                           module_id=module_id,
                                           env=env,
                                           data_ids=data_ids,
                                           family_id=experiment_config.family_id,
                                           instance_type=instance_type)
    expt_client = ExperimentClient()
    expt_info = expt_client.create(experiment_request)
    floyd_logger.debug("Created job : %s", expt_info['id'])

    job_name = normalize_job_name(expt_info['name'])
    floyd_logger.info("")
    table_output = [["JOB NAME"], [job_name]]
    floyd_logger.info(tabulate(table_output, headers="firstrow"))
    floyd_logger.info("")
    show_new_job_info(expt_client, job_name, expt_info, mode, open_notebook)


def get_command_line(instance_type, env, message, data, mode, open_notebook, tensorboard, command_str):
    """
    Return a string representing the full floyd command entered in the command line
    """
    floyd_command = ["floyd", "run"]
    floyd_command.append('--' + INSTANCE_NAME_MAP[instance_type])
    if not env == DEFAULT_ENV:
        floyd_command += ["--env", env]
    if message:
        floyd_command += ["--message", shell_quote(message)]
    if data:
        for data_item in data:
            floyd_command += ["--data", data_item]
    if tensorboard:
        floyd_command.append("--tensorboard")
    if not mode == "job":
        floyd_command += ["--mode", mode]
        if mode == 'jupyter':
            if not open_notebook:
                floyd_command.append("--no-open")
    else:
        if command_str:
            floyd_command.append(shell_quote(command_str))
    return ' '.join(floyd_command)


@click.command()
@click.argument('job_name', nargs=1)
@click.option('--data', multiple=True, help='Data mount to override')
@click.option('--open/--no-open', 'open_notebook',
              help='Automatically open the notebook url',
              default=True)
@click.option('--env',
              help='Environment type to use',
              default=None)
@click.option('--message', '-m',
              help='Job commit message')
@click.option('--gpu', is_flag=True, help='Run on a GPU instance')
@click.option('--cpu', is_flag=True, help='Run on a CPU instance')
@click.option('--gpu+', 'gpup', is_flag=True, help='Run in a GPU+ instance')
@click.option('--cpu+', 'cpup', is_flag=True, help='Run in a CPU+ instance')
@click.argument('command', nargs=-1)
@click.pass_context
def restart(ctx, job_name, data, open_notebook, env, message, gpu, cpu, gpup, cpup, command):
    """
    Restart a given job as a new job.
    """
    parameters = {}

    expt_client = ExperimentClient()
    job = expt_client.get(job_name)

    if gpup:
        instance_type = G1P_INSTANCE_TYPE
    elif cpup:
        instance_type = C1P_INSTANCE_TYPE
    elif gpu:
        instance_type = G1_INSTANCE_TYPE
    elif cpu:
        instance_type = C1_INSTANCE_TYPE
    else:
        instance_type = job.instance_type

    if instance_type is not None:
        parameters['instance_type'] = instance_type
    else:
        instance_type = job.instance_type

    if env is not None:
        if not validate_env(env, instance_type):
            sys.exit(1)
        parameters['env'] = env

    success, data_ids = process_data_ids(data)
    if not success:
        sys.exit(1)

    if message:
        parameters['message'] = message

    if command:
        parameters['command'] = ' '.join(command)

    floyd_logger.info('Restarting job %s...', job_name)

    new_job_info = expt_client.restart(job.id, parameters=parameters)
    if not new_job_info:
        floyd_logger.error("Failed to restart job")
        sys.exit(1)

    floyd_logger.info('New job created:')
    table_output = [["JOB NAME"], [new_job_info['name']]]
    floyd_logger.info('\n' + tabulate(table_output, headers="firstrow") + '\n')

    show_new_job_info(expt_client, new_job_info['name'], new_job_info, job.mode, open_notebook)
