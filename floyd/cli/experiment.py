import click
import webbrowser
from tabulate import tabulate

import floyd
from floyd.client.common import get_url_contents
from floyd.client.experiment import ExperimentClient
from floyd.client.task_instance import TaskInstanceClient
from floyd.config import ExperimentConfigManager, FloydIgnoreManager, generate_uuid
from floyd.model.experiment_config import ExperimentConfig
from floyd.log import logger as floyd_logger


@click.command()
@click.option('--project', prompt=True, required=True, help='Project name')
def init(project):
    experiment_config = ExperimentConfig(name=project,
                                         family_id=generate_uuid())
    ExperimentConfigManager.set_config(experiment_config)
    FloydIgnoreManager.init()
    floyd_logger.info("Project {} initialized in current directory".format(project))


@click.command()
@click.argument('id', required=False, nargs=1)
def ps(id):
    if id:
        experiment = ExperimentClient().get(id)
        print_experiments([experiment])
    else:
        experiments = ExperimentClient().get_all()
        print_experiments(experiments)


def print_experiments(experiments):
    headers = ["RUN ID", "CREATED", "STATUS", "DURATION(s)", "NAME", "VERSION"]
    expt_list = []
    for experiment in experiments:
        expt_list.append([experiment.id, experiment.created, experiment.state,
                          experiment.duration, experiment.name, experiment.description])
    floyd_logger.info(tabulate(expt_list, headers=headers))


@click.command()
@click.option('-u', '--url', is_flag=True, default=False, help='Only print url for accessing logs')
@click.argument('id', nargs=1)
def logs(id, url):
    experiment = ExperimentClient().get(id)
    task_instance = TaskInstanceClient().get(experiment.task_instances[0])
    log_url = "{}/api/v1/resources/{}?content=true".format(floyd.floyd_host, task_instance.log_id)
    if url:
        floyd_logger.info(log_url)
        return
    log_file_contents = get_url_contents(log_url)
    floyd_logger.info(log_file_contents)


@click.command()
@click.option('-u', '--url', is_flag=True, default=False, help='Only print url for accessing logs')
@click.argument('id', nargs=1)
def output(id, url):
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
    experiment = ExperimentClient().get(id)
    if experiment.state not in ["queued", "running"]:
        floyd_logger.info("Experiment in {} state cannot be stopped".format(experiment.state))
        return

    if ExperimentClient().stop(id):
        floyd_logger.info("Experiment stopped")
    else:
        floyd_logger.error("Failed to stop experiment")
