import click
import webbrowser
from tabulate import tabulate
from time import sleep

import floyd
from floyd.client.common import get_url_contents
from floyd.client.experiment import ExperimentClient
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
    floyd_logger.info("""
    You can now run your code in Floyd by:
        floyd run "python 1_Introduction/helloworld.py"
    """)


@click.command()
@click.argument('id', required=False, nargs=1)
def status(id):
    """
    Show the status of a run with id.
    It can also list status of all the runs in the project.
    """
    if id:
        experiment = ExperimentClient().get(id)
        print_experiments([experiment])
    else:
        experiments = ExperimentClient().get_all()
        print_experiments(experiments)


def print_experiments(experiments):
    headers = ["RUN ID", "CREATED", "STATUS", "DURATION(s)", "NAME", "INSTANCE", "VERSION"]
    expt_list = []
    for experiment in experiments:
        expt_list.append([experiment.id, experiment.created_pretty, experiment.state,
                          experiment.duration_rounded, experiment.name,
                          experiment.instance_type_trimmed, experiment.description])
    floyd_logger.info(tabulate(expt_list, headers=headers))


@click.command()
@click.option('-u', '--url', is_flag=True, default=False, help='Only print url for accessing logs')
@click.option('-t', '--tail', is_flag=True, default=False, help='Stream the logs')
@click.argument('id', nargs=1)
def logs(id, url, tail, sleep_duration=1):
    """
    Print the logs of the run.
    """
    experiment = ExperimentClient().get(id)
    task_instance = TaskInstanceClient().get(experiment.task_instances[0])
    log_url = "{}/api/v1/resources/{}?content=true".format(floyd.floyd_host, task_instance.log_id)
    if url:
        floyd_logger.info(log_url)
        return
    if tail:
        floyd_logger.info("Waiting for logs ...")
        current_shell_output = ""
        has_output_started = False
        has_output_ended = False
        OUTPUT_MARKER = '#' * 80

        while True:
            # Get the logs in a loop and log the new lines
            log_file_contents = get_url_contents(log_url)
            print_output = log_file_contents[len(current_shell_output):]
            if len(print_output.strip()):
                if OUTPUT_MARKER in print_output:
                    if not has_output_started:
                        print_output = print_output.split(OUTPUT_MARKER)[1]
                        has_output_started = True
                    elif not has_output_ended:
                        print("OUTPUT ENDED")
                        print(print_output)
                        print_output = print_output.split(OUTPUT_MARKER)[0]
                        has_output_ended = True
                if has_output_started:
                    floyd_logger.info(print_output)
                if has_output_ended:
                    break
            current_shell_output = log_file_contents
            sleep(sleep_duration)
    else:
        log_file_contents = get_url_contents(log_url)
        if len(log_file_contents.strip()):
            floyd_logger.info(log_file_contents)
        else:
            floyd_logger.info("No logs available yet. Try after a few seconds.")


@click.command()
@click.option('-u', '--url', is_flag=True, default=False, help='Only print url for accessing logs')
@click.argument('id', nargs=1)
def output(id, url):
    """
    Shows the output url of the run.
    By default opens the output page in your default browser.
    """
    experiment = ExperimentClient().get(id)
    task_instance = TaskInstanceClient().get(experiment.task_instances[0])
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
