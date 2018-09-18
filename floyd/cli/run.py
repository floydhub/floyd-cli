from __future__ import print_function
import click
from tabulate import tabulate
from time import sleep
import webbrowser
import sys
import yaml
try:
    from pipes import quote as shell_quote
except ImportError:
    from shlex import quote as shell_quote

import floyd
from floyd.constants import (
    DEFAULT_ENV,
    INSTANCE_NAME_MAP,
    INSTANCE_TYPE_MAP,
)
from floyd.client.data import DataClient
from floyd.client.project import ProjectClient
from floyd.cli.utils import (
    get_data_name, normalize_data_name, normalize_job_name
)
from floyd.client.experiment import ExperimentClient
from floyd.client.module import ModuleClient
from floyd.client.env import EnvClient
from floyd.exceptions import FloydException
from floyd.manager.auth_config import AuthConfigManager
from floyd.manager.experiment_config import ExperimentConfigManager
from floyd.constants import (
    G1P_INSTANCE_TYPE, C1P_INSTANCE_TYPE, C1_INSTANCE_TYPE, G1_INSTANCE_TYPE,
    INSTANCE_ARCH_MAP, G2_INSTANCE_TYPE, C2_INSTANCE_TYPE
)
from floyd.model.module import Module
from floyd.model.experiment import ExperimentRequest
from floyd.log import logger as floyd_logger
from floyd.exceptions import BadRequestException
from floyd.cli.experiment import get_log_id, follow_logs
from floyd.cli.utils import read_yaml_config


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
            data_name_or_id = normalize_data_name(data_name_or_id, use_data_config=False)

        data_obj = DataClient().get(normalize_data_name(data_name_or_id, use_data_config=False))

        if not data_obj:
            # Try with the raw ID
            data_obj = DataClient().get(data_name_or_id)

        if not data_obj:
            floyd_logger.error("Data not found for name or id: {}".format(data_name_or_id))
            return False, None
        if path:
            data_ids.append("%s:%s" % (data_obj.id, path))
        else:
            data_ids.append(data_obj.id)
    return True, data_ids


def resolve_final_instance_type(instance_type_override, yaml_str, task, cli_default):
    if instance_type_override:
        return instance_type_override

    yaml_config = None
    if yaml_str:
        try:
            yaml_config = yaml.safe_load(yaml_str)
        except Exception as e:
            floyd_logger.info("Error reading floyd config file:\n\n%s\nSee https://docs.floydhub.com/floyd_config for more info.", e)
            sys.exit(1)

    if yaml_config:
        machine = yaml_config.get('machine')
        if task:
            machine = yaml_config.get('task', {}).get(task, {}).get('machine', machine)
        if machine:
            return INSTANCE_TYPE_MAP[machine]
    return cli_default['instance_type']


def validate_env(env, arch):
    env_map = EnvClient().get_all()
    envs = env_map.get(arch)
    if envs:
        if env not in envs:
            envlist = tabulate([
                [env_name]
                for env_name in sorted(envs.keys())
            ])
            floyd_logger.error("%s is not in the list of supported environments:\n%s", env, envlist)
            return False
    else:
        floyd_logger.error("invalid instance type")
        return False

    return True


def show_new_job_info(expt_client, job_name, expt_info, mode, open_notebook=True):
    table_output = [["JOB NAME"], [job_name]]
    floyd_logger.info('\n' + tabulate(table_output, headers="firstrow") + '\n')

    job_url = '%s/%s' % (floyd.floyd_web_host, job_name)
    floyd_logger.info("URL to job: %s", job_url)

    if mode == 'jupyter':
        floyd_logger.info("\n[!] DEPRECATION NOTICE\n"
                          "Jupyter mode will no longer be supported after September 15th.\n"
                          "Please migrate your projects to use Workspaces: "
                          "https://docs.floydhub.com/guides/workspace/.")

    if mode in ['jupyter', 'serve']:
        while True:
            # Wait for the experiment / task instances to become available
            try:
                experiment = expt_client.get(expt_info['id'])
                if experiment.task_instances:
                    break
            except Exception:
                pass

            floyd_logger.debug("Job not available yet: %s", expt_info['id'])
            sleep(3)
            continue

        # Print the url to jupyter notebook
        if mode == 'jupyter':
            if not experiment.service_url:
                floyd_logger.error("Jupyter not available, please check job state and log for error.")
                sys.exit(1)

            if open_notebook:
                webbrowser.open(job_url)

        # Print the url to serving endpoint
        if mode == 'serve':
            floyd_logger.info("URL to service endpoint: %s", experiment.service_url)

        if experiment.timeout_seconds < 24 * 60 * 60:
            floyd_logger.info("\nYour job timeout is currently set to %s seconds",
                              experiment.timeout_seconds)
            floyd_logger.info("This is because you are in the free plan. Paid users will have longer timeouts. "
                              "See https://www.floydhub.com/pricing for details")

    else:
        floyd_logger.info("\nTo view logs enter:")
        floyd_logger.info("   floyd logs %s", job_name)


@click.command()
# To enforce having a single --env, we have to allow multiple --env flags and
# then manually enforce that just one was passed. Otherwise all but the last
# --env will just be ignored. This is a way around the limitations of click's
# behavior.
@click.option('--env',
              help='Environment name to use. Eg: tensorflow-1.8',
              default=None,
              multiple=True)
@click.option('--gpu', is_flag=True, default=False, help='Run on a GPU instance')
@click.option('--data', multiple=True, help='Dataset name and path to attach to the job')
@click.option('--message', '-m',
              help='Specify description for the job')
@click.option('--mode',
              help='Select the mode for this run',
              default=None,
              type=click.Choice(['job', 'jupyter', 'serve']))
@click.option('-f', '--follow', is_flag=True, default=False, help='Automatically follow logs')
@click.option('--tensorboard/--no-tensorboard',
              help='Enable tensorboard in the job environment')
@click.option('--cpu', is_flag=True, default=False, help='Run on a CPU instance')
@click.option('--gpu+', 'gpup', is_flag=True, help='Run in a GPU+ instance')
@click.option('--cpu+', 'cpup', is_flag=True, help='Run in a CPU+ instance')
@click.option('--gpu2', 'gpu2', is_flag=True, help='Run in a GPU2 instance')
@click.option('--cpu2', 'cpu2', is_flag=True, help='Run in a CPU2 instance')
@click.option('--max-runtime', '-r', help='Max runtime after which job is terminated, in seconds')
@click.option('--task', help='Run a specified task defined in floyd config file')
@click.option('--open/--no-open', 'open_notebook',
              help='Automatically open the notebook url',
              default=True)
@click.argument('command', nargs=-1)
@click.pass_context
def run(ctx, cpu, gpu, env, message, data, mode, open_notebook, follow, tensorboard, gpup, cpup, gpu2, cpu2, max_runtime, task, command):
    """
    Start a new job on FloydHub.

    Floyd will upload contents of the current directory and
    run your command.
    """
    # cli_default is used for any option that has default value
    cli_default = {'description': '', 'command': ''}
    # Error early if more than one --env is passed.  Then get the first/only
    # --env out of the list so all other operations work normally (they don't
    # expect an iterable). For details on this approach, see the comment above
    # the --env click option
    if not env:
        cli_default['env'] = DEFAULT_ENV
        env = None
    elif len(env) > 1:
        floyd_logger.error(
            "You passed more than one environment: {}. Please specify a single environment.".format(env)
        )
        sys.exit(1)
    else:
        env = env[0]

    if not mode:
        cli_default['mode'] = 'command'

    experiment_config = ExperimentConfigManager.get_config()
    access_token = AuthConfigManager.get_access_token()
    namespace = experiment_config.namespace or access_token.username

    if not ProjectClient().exists(experiment_config.name, namespace=namespace):
        floyd_logger.error('Invalid project id, please run '
                           '"floyd init PROJECT_NAME" before scheduling a job.')
        sys.exit(1)

    experiment_name = "{}/{}".format(namespace, experiment_config.name)

    success, data_ids = process_data_ids(data)
    if not success:
        sys.exit(2)

    # Create module
    default_name = 'input' if len(data_ids) <= 1 else None
    module_inputs = [{'name': get_data_name(data_str, default_name),
                      'type': 'dir'} for data_str in data_ids]

    instance_type = None
    if gpu2:
        instance_type = G2_INSTANCE_TYPE
    elif cpu2:
        instance_type = C2_INSTANCE_TYPE
    elif gpup:
        instance_type = G1P_INSTANCE_TYPE
    elif cpup:
        instance_type = C1P_INSTANCE_TYPE
    elif gpu:
        instance_type = G1_INSTANCE_TYPE
    elif cpu:
        instance_type = C1_INSTANCE_TYPE

    if not instance_type:
        cli_default['instance_type'] = C1_INSTANCE_TYPE

    yaml_config = read_yaml_config()
    arch = INSTANCE_ARCH_MAP[
        resolve_final_instance_type(instance_type, yaml_config, task, cli_default)
    ]
    if not validate_env(env or cli_default['env'], arch):
        sys.exit(3)

    command_str = ' '.join(command)
    if command_str and mode in ('jupyter', 'serve'):
        floyd_logger.error('Command argument "%s" cannot be used with mode: %s.\nSee http://docs.floydhub.com/guides/run_a_job/#mode for more information about run modes.', command_str, mode)  # noqa
        sys.exit(3)
    if command_str == '':
        # set to none so it won't override floyd config
        command_str = None

    module = Module(name=experiment_name,
                    description=message or '',
                    command=command_str,
                    mode=mode,
                    enable_tensorboard=tensorboard,
                    family_id=experiment_config.family_id,
                    inputs=module_inputs,
                    env=env,
                    instance_type=instance_type,
                    yaml_config=yaml_config,
                    task=task)

    try:
        module_id = ModuleClient().create(module, cli_default)
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
    if max_runtime:
        max_runtime = int(max_runtime)
    full_command = get_command_line(instance_type, env, message, data, mode, open_notebook, tensorboard, command_str)
    experiment_request = ExperimentRequest(name=experiment_name,
                                           description=message,
                                           full_command=full_command,
                                           module_id=module_id,
                                           max_runtime=max_runtime,
                                           env=env,
                                           data_ids=data_ids,
                                           family_id=experiment_config.family_id,
                                           instance_type=instance_type,
                                           yaml_config=yaml_config,
                                           task=task)
    expt_client = ExperimentClient()
    expt_info = expt_client.create(experiment_request, cli_default)
    floyd_logger.debug("Created job : %s", expt_info['id'])

    job_name = expt_info['name']
    if not follow:
        show_new_job_info(expt_client, job_name, expt_info, mode, open_notebook)
    else:
        # If the user specified --follow, we assume they're only interested in
        # log output and not in anything that would be displayed by
        # show_new_job_info.
        floyd_logger.info("Opening logs ...")
        instance_log_id = instance_log_id = get_log_id(job_name)
        follow_logs(instance_log_id)


def get_command_line(instance_type, env, message, data, mode, open_notebook, tensorboard, command_str):
    """
    Return a string representing the full floyd command entered in the command line
    """
    floyd_command = ["floyd", "run"]
    if instance_type:
        floyd_command.append('--' + INSTANCE_NAME_MAP[instance_type])
    if env and not env == DEFAULT_ENV:
        floyd_command += ["--env", env]
    if message:
        floyd_command += ["--message", shell_quote(message)]
    if data:
        for data_item in data:
            parts = data_item.split(':')

            if len(parts) > 1:
                data_item = normalize_data_name(parts[0], use_data_config=False) + ':' + parts[1]

            floyd_command += ["--data", data_item]
    if tensorboard:
        floyd_command.append("--tensorboard")
    if mode and mode != "job":
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
# To enforce having a single --env, we have to allow multiple --env flags and
# then manually enforce that just one was passed. Otherwise all but the last
# --env will just be ignored. This is a way around the limitations of click's
# behavior.
@click.option('--env',
              help='Environment type to use',
              default=[None],
              multiple=True)
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
    Restart a finished job as a new job.
    """
    # Error early if more than one --env is passed. Then get the first/only
    # --env out of the list so all other operations work normally (they don't
    # expect an iterable). For details on this approach, see the comment above
    # the --env click option
    if len(env) > 1:
        floyd_logger.error(
            "You passed more than one environment: {}. Please specify a single environment.".format(env)
        )
        sys.exit(1)
    env = env[0]

    parameters = {}

    expt_client = ExperimentClient()

    try:
        job = expt_client.get(normalize_job_name(job_name))
    except FloydException:
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
        arch = INSTANCE_ARCH_MAP[instance_type]
        if not validate_env(env, arch):
            sys.exit(1)
        parameters['env'] = env

    success, data_ids = process_data_ids(data)
    if not success:
        sys.exit(1)
    if data_ids:
        parameters['data_ids'] = data_ids

    if message:
        parameters['description'] = message

    if command:
        parameters['command'] = ' '.join(command)

    floyd_logger.info('Restarting job %s...', job_name)

    new_job_info = expt_client.restart(job.id, parameters=parameters)
    if not new_job_info:
        floyd_logger.error("Failed to restart job")
        sys.exit(1)

    show_new_job_info(expt_client, new_job_info['name'], new_job_info, job.mode, open_notebook)
