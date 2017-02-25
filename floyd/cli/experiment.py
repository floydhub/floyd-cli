import click
import webbrowser
from tabulate import tabulate
from time import sleep

import floyd
from floyd.cli.utils import get_task_url, get_module_task_instance_id
from floyd.client.common import get_url_contents
from floyd.client.experiment import ExperimentClient
from floyd.client.module import ModuleClient
from floyd.client.task_instance import TaskInstanceClient
from floyd.config import generate_uuid
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
    experiment_config = ExperimentConfig(name=project,
                                         family_id=generate_uuid())
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
    headers = ["RUN ID", "CREATED", "STATUS", "DURATION(s)", "NAME", "INSTANCE", "VERSION"]
    expt_list = []
    for experiment in experiments:
        expt_list.append([experiment.id, experiment.created_pretty, experiment.state,
                          experiment.duration_rounded, experiment.name,
                          experiment.instance_type_trimmed, experiment.description])
    floyd_logger.info(tabulate(expt_list, headers=headers))


@click.command()
@click.argument('id', nargs=1)
def info(id):
    """
    Prints detailed info for the run
    """
    experiment = ExperimentClient().get(id)
    task_instance = TaskInstanceClient().get(get_module_task_instance_id(experiment.task_instances))
    mode = url = None
    if experiment.state == "running":
        if task_instance.mode in ['jupyter', 'serving']:
            mode = task_instance.mode
            url = get_task_url(task_instance.id)
    table = [["Run ID", experiment.id], ["Name", experiment.name], ["Created", experiment.created_pretty],
             ["Status", experiment.state], ["Duration(s)", experiment.duration_rounded],
             ["Output ID", task_instance.id], ["Instance", experiment.instance_type_trimmed],
             ["Version", experiment.description]]
    if mode:
        table.append(["Mode", mode])
    if url:
        table.append(["Url", url])
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
    task_instance = TaskInstanceClient().get(get_module_task_instance_id(experiment.task_instances))
    log_url = "{}/api/v1/resources/{}?content=true".format(floyd.floyd_host, task_instance.log_id)
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
@click.argument('id', nargs=1)
def output(id, url):
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

    if ExperimentClient().stop(id):
        floyd_logger.info("Experiment shutdown request submitted. Check status to confirm shutdown")
    else:
        floyd_logger.error("Failed to stop experiment")


@click.command()
@click.argument('id', nargs=1)
@click.option('-y', '--yes', is_flag=True, default=False, help='Skip confirmation')
def delete(id, yes):
    """
    Delete project run
    """
    experiment = ExperimentClient().get(id)
    task_instance = TaskInstanceClient().get(get_module_task_instance_id(experiment.task_instances))

    if experiment.state in ["queued", "running"]:
        floyd_logger.info("Experiment in {} state cannot be deleted. Stop it first".format(experiment.state))
        return

    if not yes:
        click.confirm('Delete Run: {}?'.format(experiment.name), abort=True, default=False)

    if task_instance.module_id:
        ModuleClient().delete(task_instance.module_id)

    if ExperimentClient().delete(id):
        floyd_logger.info("Experiment deleted")
    else:
        floyd_logger.error("Failed to delete experiment")
