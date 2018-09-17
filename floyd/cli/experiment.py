import click
from tabulate import tabulate
from time import sleep
import webbrowser
import sys
from shutil import copyfile
import os

import floyd
from floyd.cli.utils import (
    get_module_task_instance_id,
    normalize_job_name,
    get_namespace_from_name
)
from floyd.client.experiment import ExperimentClient
from floyd.client.module import ModuleClient
from floyd.client.project import ProjectClient
from floyd.client.resource import ResourceClient
from floyd.client.task_instance import TaskInstanceClient
from floyd.exceptions import FloydException
from floyd.manager.experiment_config import ExperimentConfigManager
from floyd.manager.floyd_ignore import FloydIgnoreManager
from floyd.model.experiment_config import ExperimentConfig
from floyd.log import logger as floyd_logger
from floyd.cli.utils import read_yaml_config


@click.command()
@click.argument('project_name', nargs=1)
def init(project_name):
    """
    Initialize new project at the current path.

    After this you can run other FloydHub commands like status and run.
    """

    project_obj = ProjectClient().get_by_name(project_name)

    if not project_obj:
        namespace, name = get_namespace_from_name(project_name)
        create_project_base_url = "{}/projects/create".format(floyd.floyd_web_host)
        create_project_url = "{}?name={}&namespace={}".format(create_project_base_url, name, namespace)
        floyd_logger.info(('Project name does not yet exist on floydhub.com. '
                          'Create your new project on floydhub.com:\n\t%s'),
                          create_project_base_url)
        webbrowser.open(create_project_url)

        name = click.prompt('Press ENTER to use project name "%s" or enter a different name' % project_name, default=project_name, show_default=False)

        project_name = name.strip() or project_name
        project_obj = ProjectClient().get_by_name(project_name)

        if not project_obj:
            raise FloydException('Project "%s" does not exist on floydhub.com. Ensure it exists before continuing.' % project_name)

    namespace, name = get_namespace_from_name(project_name)
    experiment_config = ExperimentConfig(name=name,
                                         namespace=namespace,
                                         family_id=project_obj.id)
    ExperimentConfigManager.set_config(experiment_config)
    FloydIgnoreManager.init()

    yaml_config = read_yaml_config()
    if not yaml_config:
        copyfile(os.path.join(os.path.dirname(__file__), 'default_floyd.yml'), 'floyd.yml')

    floyd_logger.info("Project \"%s\" initialized in current directory", project_name)


@click.command()
@click.argument('id', required=False, nargs=1)
def status(id):
    """
    View status of all jobs in a project.

    The command also accepts a specific job name.
    """
    if id:
        try:
            experiment = ExperimentClient().get(normalize_job_name(id))
        except FloydException:
            experiment = ExperimentClient().get(id)

        print_experiments([experiment])
    else:
        experiments = ExperimentClient().get_all()
        print_experiments(experiments)


def print_experiments(experiments):
    """
    Prints job details in a table. Includes urls and mode parameters
    """
    headers = ["JOB NAME", "CREATED", "STATUS", "DURATION(s)", "INSTANCE", "DESCRIPTION", "METRICS"]
    expt_list = []
    for experiment in experiments:
        expt_list.append([normalize_job_name(experiment.name),
                          experiment.created_pretty, experiment.state,
                          experiment.duration_rounded, experiment.instance_type_trimmed,
                          experiment.description, format_metrics(experiment.latest_metrics)])
    floyd_logger.info(tabulate(expt_list, headers=headers))


def format_metrics(latest_metrics):
    return ', '.join(
        ["%s=%s" % (k, latest_metrics[k]) for k in sorted(latest_metrics.keys())]
    ) if latest_metrics else ''


@click.command()
@click.argument('id', nargs=1)
def clone(id):
    """
    Download files from a job.

    This will download the files that were originally uploaded at
    the start of the job.
    """
    try:
        experiment = ExperimentClient().get(normalize_job_name(id, use_config=False))
    except FloydException:
        experiment = ExperimentClient().get(id)

    task_instance_id = get_module_task_instance_id(experiment.task_instances)
    task_instance = TaskInstanceClient().get(task_instance_id) if task_instance_id else None
    if not task_instance:
        sys.exit("Cannot clone this version of the job. Try a different version.")
    module = ModuleClient().get(task_instance.module_id) if task_instance else None
    code_url = "{}/api/v1/resources/{}?content=true&download=true".format(floyd.floyd_host,
                                                                          module.resource_id)
    ExperimentClient().download_tar(url=code_url,
                                    untar=True,
                                    delete_after_untar=True)


@click.command()
@click.argument('job_name_or_id', nargs=1, required=False)
def info(job_name_or_id):
    """
    View detailed information of a job.
    """
    try:
        experiment = ExperimentClient().get(normalize_job_name(job_name_or_id))
    except FloydException:
        experiment = ExperimentClient().get(job_name_or_id)

    task_instance_id = get_module_task_instance_id(experiment.task_instances)
    task_instance = TaskInstanceClient().get(task_instance_id) if task_instance_id else None
    normalized_job_name = normalize_job_name(experiment.name)
    table = [["Job name", normalized_job_name],
             ["Output name", normalized_job_name + '/output' if task_instance else None],
             ["Created", experiment.created_pretty],
             ["Status", experiment.state], ["Duration(s)", experiment.duration_rounded],
             ["Instance", experiment.instance_type_trimmed],
             ["Description", experiment.description],
             ["Metrics", format_metrics(experiment.latest_metrics)]]
    if task_instance and task_instance.mode in ['jupyter', 'serving']:
        table.append(["Mode", task_instance.mode])
        table.append(["Url", experiment.service_url])
    if experiment.tensorboard_url:
        table.append(["Tensorboard", experiment.tensorboard_url])
    floyd_logger.info(tabulate(table))


def get_log_id(job_id):
    log_msg_printed = False
    while True:
        try:
            experiment = ExperimentClient().get(normalize_job_name(job_id))
        except FloydException:
            experiment = ExperimentClient().get(job_id)

        instance_log_id = experiment.instance_log_id
        if instance_log_id:
            break
        elif not log_msg_printed:
            floyd_logger.info("Waiting for logs ...\n")
            log_msg_printed = True

        sleep(1)

    return instance_log_id


def follow_logs(instance_log_id, sleep_duration=1):
    cur_idx = 0
    while True:
        # Get the logs in a loop and log the new lines
        log_file_contents = ResourceClient().get_content(instance_log_id)
        print_output = log_file_contents[cur_idx:]
        cur_idx += len(print_output)
        sys.stdout.write(print_output)
        sleep(sleep_duration)


@click.command()
@click.option('-u', '--url', is_flag=True, default=False, help='Only print url for accessing logs')
@click.option('-t', '--tail', is_flag=True, default=False, help='Stream the logs')
@click.option('-f', '--follow', is_flag=True, default=False, help='Stream the logs (alias for -t/--tail)')
@click.argument('id', nargs=1, required=False)
def logs(id, url, tail, follow, sleep_duration=1):
    """
    View the logs of a job.

    To follow along a job in real time, use the --tail flag
    """
    tail = tail or follow

    instance_log_id = get_log_id(id)

    if url:
        log_url = "{}/api/v1/resources/{}?content=true".format(
            floyd.floyd_host, instance_log_id)
        floyd_logger.info(log_url)
        return

    if tail:
        floyd_logger.info("Launching job ...")
        follow_logs(instance_log_id, sleep_duration)
    else:
        log_file_contents = ResourceClient().get_content(instance_log_id)
        if len(log_file_contents.strip()):
            floyd_logger.info(log_file_contents.rstrip())
        else:
            floyd_logger.info("Launching job now. Try after a few seconds.")


@click.command()
@click.option('-u', '--url', is_flag=True, default=False, help='Only print url for accessing logs')
@click.argument('id', nargs=1, required=False)
def output(id, url):
    """
    View the files from a job.
    """
    try:
        experiment = ExperimentClient().get(normalize_job_name(id))
    except FloydException:
        experiment = ExperimentClient().get(id)

    output_dir_url = "%s/%s/files" % (floyd.floyd_web_host, experiment.name)
    if url:
        floyd_logger.info(output_dir_url)
    else:
        floyd_logger.info("Opening output path in your browser ...")
        webbrowser.open(output_dir_url)


@click.command()
@click.argument('id', nargs=1, required=False)
def stop(id):
    """
    Stop a running job.
    """
    try:
        experiment = ExperimentClient().get(normalize_job_name(id))
    except FloydException:
        experiment = ExperimentClient().get(id)

    if experiment.state not in ["queued", "queue_scheduled", "running"]:
        floyd_logger.info("Job in {} state cannot be stopped".format(experiment.state))
        sys.exit(1)

    if not ExperimentClient().stop(experiment.id):
        floyd_logger.error("Failed to stop job")
        sys.exit(1)

    floyd_logger.info("Experiment shutdown request submitted. Check status to confirm shutdown")


@click.command()
@click.argument('names', nargs=-1)
@click.option('-y', '--yes', is_flag=True, default=False, help='Skip confirmation')
def delete(names, yes):
    """
    Delete a training job.
    """
    failures = False
    for name in names:
        try:
            experiment = ExperimentClient().get(normalize_job_name(name))
        except FloydException:
            experiment = ExperimentClient().get(name)

        if not experiment:
            failures = True
            continue

        if not yes and not click.confirm("Delete Job: {}?".format(experiment.name),
                                         abort=False,
                                         default=False):
            floyd_logger.info("Job {}: Skipped.".format(experiment.name))
            continue

        if not ExperimentClient().delete(experiment.id):
            failures = True
        else:
            floyd_logger.info("Job %s Deleted", experiment.name)

    if failures:
        sys.exit(1)
