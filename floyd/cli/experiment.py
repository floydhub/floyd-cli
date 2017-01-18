import click

import floyd
from floyd.client.experiment import ExperimentClient
from floyd.client.task_instance import TaskInstanceClient
from floyd.logging import logger as floyd_logger


@click.command()
@click.argument('id', required=False, nargs=1)
def ps(id):
    if id:
        experiment = ExperimentClient().get(id)
        floyd_logger.info(experiment.to_dict())
    else:
        experiments = ExperimentClient().get_all()
        for experiment in experiments:
            floyd_logger.info(experiment.to_dict())


@click.command()
@click.argument('id', nargs=1)
def logs(id):
    experiment = ExperimentClient().get(id)
    task_instance = TaskInstanceClient().get(experiment.task_instances[0])
    print(task_instance.output_ids)
    log_url = "{}/api/v1/resources/{}?content=true".format(floyd.floyd_host, task_instance.log_id)
    floyd_logger.info(log_url)


@click.command()
@click.argument('id', nargs=1)
def output(id):
    experiment = ExperimentClient().get(id)
    task_instance = TaskInstanceClient().get(experiment.task_instances[0])
    if "output_dir" in task_instance.output_ids:
        output_dir_url = "{}/api/v1/resources/{}?content=true".format(floyd.floyd_host,
                                                                      task_instance.output_ids["output_dir"])
        floyd_logger.info(output_dir_url)
    else:
        floyd_logger.error("Output directory not available")


@click.command()
@click.argument('id', nargs=1)
def stop(id):
    experiment = ExperimentClient().get(id)
    if experiment.state not in ["queued", "running"]:
        floyd_logger.info("Experiment already finished")
        return

    if ExperimentClient().stop(id):
        floyd_logger.info("Experiment stopped")
    else:
        floyd_logger.error("Failed to stop experiment")
