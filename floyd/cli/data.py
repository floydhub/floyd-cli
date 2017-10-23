import click
import sys
from tabulate import tabulate
import webbrowser

import floyd
from floyd.client.data import DataClient
from floyd.client.dataset import DatasetClient
from floyd.manager.auth_config import AuthConfigManager
from floyd.manager.data_config import DataConfig, DataConfigManager
from floyd.log import logger as floyd_logger
from floyd.cli.data_upload_utils import (
    opt_to_resume, upload_is_resumable, abort_previous_upload,
    initialize_new_upload, complete_upload
)
from floyd.cli.utils import normalize_data_name


@click.group()
def data():
    """
    Subcommand for data operations
    """
    pass


@click.command()
@click.argument('dataset-name', nargs=1)
def init(dataset_name):
    """
    Initialize a new dataset at the current dir.
    After init ensure that your data files are in this directory.
    Then you can upload them to Floyd. Example:

        floyd data upload
    """
    dataset_obj = DatasetClient().get_by_name(dataset_name)
    if not dataset_obj:
        create_dataset_base_url = "{}/datasets/create".format(floyd.floyd_web_host)
        create_dataset_url = "{}?name={}".format(create_dataset_base_url, dataset_name)
        floyd_logger.error(("Dataset name does not match your list of datasets. "
                            "Create your new dataset in the web dashboard:\n\t%s"),
                           create_dataset_base_url)
        webbrowser.open(create_dataset_url)
        return

    data_config = DataConfig(name=dataset_name, family_id=dataset_obj.id)
    DataConfigManager.set_config(data_config)
    floyd_logger.info("Data source \"{}\" initialized in current directory".format(dataset_name))
    floyd_logger.info("""
    You can now upload your data to Floyd by:
        floyd data upload
    """)


@click.command()
@click.option('-r', '--resume',
              is_flag=True, default=False, help='Resume previous upload')
@click.option('--message', '-m', default='',
              help='Job commit message')
def upload(resume, message):
    """
    Upload data in the current dir to Floyd.
    """
    data_config = DataConfigManager.get_config()

    if not upload_is_resumable(data_config) or not opt_to_resume(resume):
        abort_previous_upload(data_config)
        access_token = AuthConfigManager.get_access_token()
        initialize_new_upload(data_config, access_token, message)

    complete_upload(data_config)


@click.command()
@click.argument('id', required=False, nargs=1)
def status(id):
    """
    Show the status of a run with id. or a friendly name.
    It can also list status of all the runs in the project.
    """
    if id:
        data_source = DataClient().get(id)
        print_data([data_source] if data_source else [])
    else:
        data_sources = DataClient().get_all()
        print_data(data_sources)


def print_data(data_sources):
    """
    Print data information in tabular form
    """
    if not data_sources:
        return

    headers = ["DATA NAME", "CREATED", "STATUS", "DISK USAGE"]
    data_list = []
    for data_source in data_sources:
        data_list.append([normalize_data_name(data_source.name),
                          data_source.created_pretty,
                          data_source.state, data_source.size])
    floyd_logger.info(tabulate(data_list, headers=headers))


@click.command()
@click.argument('id', nargs=1)
def clone(id):
    """
    Download the code for the job to the current path
    """
    data_source = DataClient().get(id)

    if not data_source:
        if 'output' in id:
            floyd_logger.info("Note: You cannot clone the output of a running job. You need to wait for it to finish.")
        sys.exit()

    data_url = "{}/api/v1/resources/{}?content=true&download=true".format(floyd.floyd_host,
                                                                          data_source.resource_id)
    DataClient().download_tar(url=data_url,
                              untar=True,
                              delete_after_untar=True)


@click.command()
@click.option('-u', '--url', is_flag=True, default=False,
              help='Only print url for viewing data')
@click.argument('id', nargs=1)
def output(id, url):
    """
    Shows the url of the dataset. You can use id or a friendly URI.
    By default opens the output page in your default browser.
    """
    data_source = DataClient().get(id)

    if not data_source:
        sys.exit()

    data_url = "%s/%s" % (floyd.floyd_web_host, data_source.name)
    if url:
        floyd_logger.info(data_url)
    else:
        floyd_logger.info("Opening output directory in your browser ...")
        webbrowser.open(data_url)


@click.command()
@click.argument('ids', nargs=-1)
@click.option('-y', '--yes', is_flag=True, default=False,
              help='Skip confirmation')
def delete(ids, yes):
    """
    Delete data sets.
    """
    failures = False

    for id in ids:
        data_source = DataClient().get(id)
        if not data_source:
            failures = True
            continue

        data_name = normalize_data_name(data_source.name)
        suffix = data_name.split('/')[-1]
        if not suffix.isdigit():
            failures = True
            floyd_logger.error('%s is not a dataset, skipped.', id)
            if suffix == 'output':
                floyd_logger.error('To delete job output, please delete the job itself.')
            continue

        if not yes and not click.confirm("Delete Data: {}?".format(data_name),
                                         abort=False,
                                         default=False):
            floyd_logger.info("Data %s: Skipped", data_name)
            continue

        if not DataClient().delete(data_source.id):
            failures = True
        else:
            floyd_logger.info("Data %s: Deleted", data_name)

    if failures:
        sys.exit(1)


@click.command()
@click.argument('source')
def add(source):
    """
    Create data for current dataset from a given source, for example: foo/projects/bar/1/output
    """
    new_data = DatasetClient().add_data(source)
    print_data([DataClient().get(new_data['data_id'])])


data.add_command(clone)
data.add_command(delete)
data.add_command(init)
data.add_command(upload)
data.add_command(status)
data.add_command(output)
data.add_command(add)
