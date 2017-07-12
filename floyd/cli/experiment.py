import click
from tabulate import tabulate
from time import sleep
import webbrowser
import sys

import floyd
from floyd.cli.utils import get_module_task_instance_id
from floyd.client.common import get_url_contents
from floyd.client.experiment import ExperimentClient
from floyd.client.module import ModuleClient
from floyd.client.project import ProjectClient
from floyd.client.task_instance import TaskInstanceClient
from floyd.manager.experiment_config import ExperimentConfigManager
from floyd.manager.floyd_ignore import FloydIgnoreManager
from floyd.model.experiment_config import ExperimentConfig
from floyd.log import logger as floyd_logger


@click.command()
@click.argument('project', nargs=1)
def init(project):
    """
    Initialize new project at the current dir.
    After init run your command. Example:

        floyd run python tensorflow.py > /output/model.1
    """
    project_obj = ProjectClient().get_project_matching_name(project)
    if not project_obj:
        create_project_url = "{}/projects/create".format(floyd.floyd_web_host)
        floyd_logger.error(("Project name does not match your list of projects. "
                            "Create your new project in the web dashboard:\n\t%s/projects"),
                           create_project_url)
        webbrowser.open(create_project_url)
        return

    experiment_config = ExperimentConfig(name=project,
                                         family_id=project_obj.id)
    ExperimentConfigManager.set_config(experiment_config)
    FloydIgnoreManager.init()
    floyd_logger.info("Project \"{}\" initialized in current directory".format(project))


@click.command()
@click.argument('id', required=False, nargs=1)
def status(id):
    """
    View status of all or specific run.
    It can also list status of all the runs in the project.
    """
    if id:
        experiment = ExperimentClient().get(id)
        print_experiments([experiment])
    else:
        experiments = ExperimentClient().get_all()
        print_experiments(experiments)


def print_experiments(experiments):
    """
    Prints expt details in a table. Includes urls and mode parameters
    """
    headers = ["RUN ID", "CREATED", "STATUS", "DURATION(s)", "NAME", "INSTANCE", "DESCRIPTION"]
    expt_list = []
    for experiment in experiments:
        expt_list.append([experiment.id, experiment.created_pretty, experiment.state,
                          experiment.duration_rounded, experiment.name,
                          experiment.instance_type_trimmed, experiment.description])
    floyd_logger.info(tabulate(expt_list, headers=headers))


@click.command()
@click.argument('id', nargs=1)
def clone(id):
    """
    Download the code for the experiment to the current path
    """
    experiment = ExperimentClient().get(id)
    task_instance_id = get_module_task_instance_id(experiment.task_instances)
    task_instance = TaskInstanceClient().get(task_instance_id) if task_instance_id else None
    if not task_instance:
        sys.exit("Cannot clone this version of the experiment. Try a different version.")
    module = ModuleClient().get(task_instance.module_id) if task_instance else None
    code_url = "{}/api/v1/resources/{}?content=true&download=true".format(floyd.floyd_host,
                                                                          module.resource_id)
    ExperimentClient().download_tar(url=code_url,
                                    untar=True,
                                    delete_after_untar=True)


@click.command()
@click.argument('id', nargs=1)
def info(id):
    """
    Prints detailed info for the run
    """
    experiment = ExperimentClient().get(id)
    task_instance_id = get_module_task_instance_id(experiment.task_instances)
    task_instance = TaskInstanceClient().get(task_instance_id) if task_instance_id else None
    table = [["Run ID", experiment.id], ["Name", experiment.name], ["Created", experiment.created_pretty],
             ["Status", experiment.state], ["Duration(s)", experiment.duration_rounded],
             ["Output ID", task_instance.id if task_instance else None], ["Instance", experiment.instance_type_trimmed],
             ["Version", experiment.description]]
    if task_instance and task_instance.mode in ['jupyter', 'serving']:
        table.append(["Mode", task_instance.mode])
        table.append(["Url", experiment.service_url])
    if experiment.tensorboard_url:
        table.append(["Tensorboard", experiment.tensorboard_url])
    floyd_logger.info(tabulate(table))


@click.command()
@click.option('-u', '--url', is_flag=True, default=False, help='Only print url for accessing logs')
@click.option('-t', '--tail', is_flag=True, default=False, help='Stream the logs')
@click.argument('id', nargs=1)
def logs(id, url, tail, sleep_duration=1):
    """
    Print the logs of the run.
    """
    experiment = ExperimentClient().get(id)
    if experiment.state == 'queued':
        floyd_logger.info("Experiment is currently in a queue")
        return

    task_id = get_module_task_instance_id(experiment.task_instances)
    task_instance = TaskInstanceClient().get(task_id)
    if not task_instance:
        floyd_logger.info("Experiment not started yet, no log to show.")
        sys.exit(1)

    log_url = "{}/api/v1/resources/{}?content=true".format(
        floyd.floyd_host, task_instance.log_id)
    if url:
        floyd_logger.info(log_url)
        return
    if tail:
        floyd_logger.info("Launching job ...")
        current_shell_output = ""
        while True:
            # Get the logs in a loop and log the new lines
            log_file_contents = get_url_contents(log_url)
            print_output = log_file_contents[len(current_shell_output):]
            if len(print_output.strip()):
                floyd_logger.info(print_output)
            current_shell_output = log_file_contents
            sleep(sleep_duration)
    else:
        log_file_contents = get_url_contents(log_url)
        if len(log_file_contents.strip()):
            floyd_logger.info(log_file_contents)
        else:
            floyd_logger.info("Launching job now. Try after a few seconds.")


@click.command()
@click.option('-u', '--url', is_flag=True, default=False, help='Only print url for accessing logs')
@click.option('-d', '--download', is_flag=True, default=False,
              help='Download the contents of the output to current directory')
@click.argument('id', nargs=1)
def output(id, url, download):
    """
    Shows the output url of the run.
    By default opens the output page in your default browser.
    """
    experiment = ExperimentClient().get(id)
    task_instance = TaskInstanceClient().get(get_module_task_instance_id(experiment.task_instances))
    if "output" in task_instance.output_ids:
        output_dir_url = "{}/api/v1/resources/{}?content=true".format(floyd.floyd_host,
                                                                      task_instance.output_ids["output"])
        if url:
            floyd_logger.info(output_dir_url)
        else:
            if download:
                output_dir_url = "{}&download=true".format(output_dir_url)
                ExperimentClient().download_tar(url=output_dir_url,
                                                untar=True,
                                                delete_after_untar=True)
            else:
                floyd_logger.info("Opening output directory in your browser ...")
                webbrowser.open(output_dir_url)
    else:
        floyd_logger.error("Output directory not available")


@click.command()
@click.argument('id', nargs=1)
def stop(id):
    """
    Stop a run before it can finish.
    """
    experiment = ExperimentClient().get(id)
    if experiment.state not in ["queued", "running"]:
        floyd_logger.info("Experiment in {} state cannot be stopped".format(experiment.state))
        return

    if ExperimentClient().stop(experiment.id):
        floyd_logger.info("Experiment shutdown request submitted. Check status to confirm shutdown")
    else:
        floyd_logger.error("Failed to stop experiment")


@click.command()
@click.argument('ids', nargs=-1)
@click.option('-y', '--yes', is_flag=True, default=False, help='Skip confirmation')
def delete(ids, yes):
    """
    Delete project runs
    """
    failures = False
    for id in ids:
        experiment = ExperimentClient().get(id)
        if not experiment:
            failures = True
            continue

        if not yes and not click.confirm("Delete Run: {}?".format(experiment.name),
                                         abort=False,
                                         default=False):
            floyd_logger.info("Experiment {}: Skipped.".format(experiment.name))
            continue

        if not ExperimentClient().delete(experiment.id):
            failures = True

    if failures:
        sys.exit(1)
