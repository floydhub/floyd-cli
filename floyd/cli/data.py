import click
from tabulate import tabulate

from floyd.client.data import DataClient
from floyd.config import AuthConfigManager, generate_uuid
from floyd.manager.data_config import DataConfig, DataConfigManager
from floyd.model.data import Data
from floyd.log import logger as floyd_logger


@click.group()
def data():
    """
    Subcommand for data operations
    """
    pass


@click.command()
@click.argument('name', nargs=1)
def init(name):
    """
    Initialize a new data upload.
    After init ensure that your data files are in this directory.
    Then you can upload them to Floyd. Example:

        floyd data upload
    """
    data_config = DataConfig(name=name, family_id=generate_uuid())
    DataConfigManager.set_config(data_config)
    floyd_logger.info("Data source \"{}\" initialized in current directory".format(name))
    floyd_logger.info("""
    You can now upload your data to Floyd by:
        floyd data upload
    """)


@click.command()
def upload():
    """
    Upload data in the current dir to Floyd.
    """
    data_config = DataConfigManager.get_config()
    access_token = AuthConfigManager.get_access_token()
    version = data_config.version

    # Create data object
    data_name = "{}/{}:{}".format(access_token.username,
                                  data_config.name,
                                  version)
    data = Data(name=data_name,
                description=version,
                version=version)
    data_id = DataClient().create(data)
    floyd_logger.debug("Created data with id : {}".format(data_id))
    floyd_logger.info("Data upload finished")

    # Update expt config including predecessor
    data_config.increment_version()
    data_config.set_data_predecessor(data_id)
    DataConfigManager.set_config(data_config)

    # Print output
    table_output = [["DATA ID", "NAME", "VERSION"],
                    [data_id, data_name, version]]
    floyd_logger.info(tabulate(table_output, headers="firstrow"))

data.add_command(init)
data.add_command(upload)

#
# def print_experiments(experiments):
#     headers = ["RUN ID", "CREATED", "STATUS", "DURATION(s)", "NAME", "INSTANCE", "VERSION"]
#     expt_list = []
#     for experiment in experiments:
#         expt_list.append([experiment.id, experiment.created_pretty, experiment.state,
#                           experiment.duration_rounded, experiment.name,
#                           experiment.instance_type_trimmed, experiment.description])
#     floyd_logger.info(tabulate(expt_list, headers=headers))
#
#
# @click.command()
# @click.option('-u', '--url', is_flag=True, default=False, help='Only print url for accessing logs')
# @click.argument('id', nargs=1)
# def logs(id, url):
#     """
#     Print the logs of the run.
#     """
#     experiment = ExperimentClient().get(id)
#     task_instance = TaskInstanceClient().get(experiment.task_instances[0])
#     log_url = "{}/api/v1/resources/{}?content=true".format(floyd.floyd_host, task_instance.log_id)
#     if url:
#         floyd_logger.info(log_url)
#         return
#     log_file_contents = get_url_contents(log_url)
#     if len(log_file_contents.strip()):
#         floyd_logger.info(log_file_contents)
#     else:
#         floyd_logger.info("No logs available yet. Try after a few seconds.")
#
#
# @click.command()
# @click.option('-u', '--url', is_flag=True, default=False, help='Only print url for accessing logs')
# @click.argument('id', nargs=1)
# def output(id, url):
#     """
#     Shows the output url of the run.
#     By default opens the output page in your default browser.
#     """
#     experiment = ExperimentClient().get(id)
#     task_instance = TaskInstanceClient().get(experiment.task_instances[0])
#     if "output" in task_instance.output_ids:
#         output_dir_url = "{}/api/v1/resources/{}?content=true".format(floyd.floyd_host,
#                                                                       task_instance.output_ids["output"])
#         if url:
#             floyd_logger.info(output_dir_url)
#         else:
#             floyd_logger.info("Opening output directory in your browser ...")
#             webbrowser.open(output_dir_url)
#     else:
#         floyd_logger.error("Output directory not available")
#
#
# @click.command()
# @click.argument('id', nargs=1)
# def stop(id):
#     """
#     Stop a run before it can finish.
#     """
#     experiment = ExperimentClient().get(id)
#     if experiment.state not in ["queued", "running"]:
#         floyd_logger.info("Experiment in {} state cannot be stopped".format(experiment.state))
#         return
#
#     if ExperimentClient().stop(id):
#         floyd_logger.info("Experiment shutdown request submitted. Check status to confirm shutdown")
#     else:
#         floyd_logger.error("Failed to stop experiment")
