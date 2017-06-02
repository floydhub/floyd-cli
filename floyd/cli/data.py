import click
import os
import sys
from tabulate import tabulate
import tempfile
import webbrowser

import floyd
from floyd.client.data import DataClient
from floyd.config import generate_uuid
from floyd.client.files import create_tarfile, sizeof_fmt
from floyd.manager.auth_config import AuthConfigManager
from floyd.manager.data_config import DataConfig, DataConfigManager
from floyd.model.data import DataRequest
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
@click.option('-r', '--resume', is_flag=True, default=False, help='Resume previous upload')
def upload(resume):
    """
    Upload data in the current dir to Floyd.
    """
    data_config = DataConfigManager.get_config()
    access_token = AuthConfigManager.get_access_token()
    data_path = data_config.data_path or ""
    version = data_config.version
    data_name = "{}/{}:{}".format(access_token.username,
                                  data_config.name,
                                  version)

    if not os.path.isfile(data_path):
        # A previous data tarball was not found.
        # Starting the upload process from scratch

        data_config.set_data_path("")
        # Create data object
        data = DataRequest(name=data_name,
                           description=version,
                           data_type='gzip',
                           version=version)
        data_id = DataClient().create(data)
        if not data_id:
            exit(1)

        # Create tarfile
        temp_dir = tempfile.mkdtemp()
        data_path = os.path.join(temp_dir, "{}.data.tar.gz".format(data_id))

        floyd_logger.debug("Creating tarfile with contents of current directory: {}".format(data_path))
        floyd_logger.info("Compressing data...")

        create_tarfile(source_dir='.', filename=data_path)

        total_file_size = os.path.getsize(data_path)

        data_config.increment_version()
        floyd_logger.info("Uploading compressed data. Total upload size: {}".format(sizeof_fmt(total_file_size)))
    data_id = data_config.data_predecessor


    floyd_logger.debug("Created data with id : {}".format(data_id))
    floyd_logger.info("Upload finished")

    # Update expt config including predecessor
    data_config.set_data_predecessor(data_id)
    data_config.set_data_path(data_path)
    DataConfigManager.set_config(data_config)

    # Print output
    table_output = [["DATA ID", "NAME", "VERSION"],
                    [data_id, data_name, version]]
    floyd_logger.info(tabulate(table_output, headers="firstrow"))


@click.command()
@click.argument('id', required=False, nargs=1)
def status(id):
    """
    Show the status of a run with id.
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

    headers = ["DATA ID", "CREATED", "DISK USAGE", "NAME", "VERSION"]
    data_list = []
    for data_source in data_sources:
        data_list.append([data_source.id, data_source.created_pretty,
                          data_source.size, data_source.name, data_source.version])
    floyd_logger.info(tabulate(data_list, headers=headers))


@click.command()
@click.option('-u', '--url', is_flag=True, default=False, help='Only print url for viewing data')
@click.argument('id', nargs=1)
def output(id, url):
    """
    Shows the output url of the run.
    By default opens the output page in your default browser.
    """
    data_source = DataClient().get(id)

    if not data_source:
        sys.exit()

    data_url = "{}/api/v1/resources/{}?content=true".format(floyd.floyd_host,
                                                            data_source.resource_id)
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

        if not yes and not click.confirm("Delete Data: {}?".format(data_source.name),
                                         abort=False,
                                         default=False):
            floyd_logger.info("Data {}: Skipped".format(data_source.name))
            continue

        if not DataClient().delete(id):
            failures = True

    if failures:
        sys.exit(1)

data.add_command(delete)
data.add_command(init)
data.add_command(upload)
data.add_command(status)
data.add_command(output)
