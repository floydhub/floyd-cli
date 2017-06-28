import click
import os
import sys
from tabulate import tabulate
import tempfile
from shutil import rmtree

from floyd.client.data import DataClient
from floyd.client.files import create_tarfile, sizeof_fmt
from floyd.client.tus_data import TusDataClient
from floyd.log import logger as floyd_logger
from floyd.manager.data_config import DataConfigManager
from floyd.model.data import DataRequest


def opt_to_resume(resume_flag):
    if resume_flag:
        return True

    msg = "An unfinished upload exists. Would you like to resume it?"
    return click.confirm(msg, abort=False, default=False)


def upload_is_resumable(data_config):
    # TODO: Check to make sure server says the upload is resumable
    return os.path.isfile(data_config.tarball_path or "") and data_config.data_endpoint


def initialize_new_upload(data_config, access_token):
    data_config.increment_version()
    version = data_config.version
    data_name = "{}/{}:{}".format(access_token.username,
                                  data_config.name,
                                  version)

    # Create data object using API
    data = DataRequest(name=data_name,
                       description=version,
                       data_type='gzip',
                       version=version)
    data_id = DataClient().create(data)
    if not data_id:
        sys.exit(1)

    data_config.set_data_predecessor(data_id)
    DataConfigManager.set_config(data_config)

    # Create tarball of the data using the ID returned from the API
    temp_dir = tempfile.mkdtemp()
    tarball_path = os.path.join(temp_dir, "{}.data.tar.gz".format(data_id))

    floyd_logger.debug("Creating tarfile with contents of current directory: %s",
                       tarball_path)
    floyd_logger.info("Compressing data...")

    create_tarfile(source_dir='.', filename=tarball_path)

    # If starting a new upload fails for some reason down the line, we don't
    # want to re-tar, so save off the tarball path now
    data_config.set_tarball_path(tarball_path)
    DataConfigManager.set_config(data_config)

    creds = DataClient().new_tus_credentials(data_id)
    if not creds:
        # TODO: delete module from server?
        floyd_logger.error("Failed to fetch upload credential from Floydhub!")
        rmtree(temp_dir)
        sys.exit(1)

    data_resource_id = creds[0]
    data_endpoint = TusDataClient().initialize_upload(
        tarball_path,
        metadata={"filename": data_resource_id},
        auth=creds)
    if not data_endpoint:
        # TODO: delete module from server?
        floyd_logger.error("Failed to get upload URL from Floydhub!")
        rmtree(temp_dir)
        sys.exit(1)

    data_config.set_data_endpoint(data_endpoint)
    DataConfigManager.set_config(data_config)


def complete_upload(data_config):
    data_endpoint = data_config.data_endpoint
    data_id = data_config.data_predecessor
    tarball_path = data_config.tarball_path
    file_size = os.path.getsize(tarball_path)

    floyd_logger.debug("Getting fresh upload credentials")
    creds = DataClient().new_tus_credentials(data_id)

    floyd_logger.info("Uploading compressed data. Total upload size: %s",
                      sizeof_fmt(file_size))

    tus_client = TusDataClient()
    if not tus_client.resume_upload(tarball_path, data_endpoint, auth=creds):
        floyd_logger.error("Failed to finish upload!")
        return

    try:
        floyd_logger.info("Removing compressed data...")
        rmtree(os.path.dirname(tarball_path))
    except (OSError, TypeError):
        pass

    data_id = data_config.data_predecessor
    floyd_logger.debug("Created data with id : %s", data_id)
    floyd_logger.info("Upload finished")

    # Update data config
    data_config.set_data_predecessor(data_id)
    data_config.set_tarball_path("")
    data_config.set_data_endpoint("")
    DataConfigManager.set_config(data_config)

    # Print output
    table_output = [["DATA ID", "NAME", "VERSION"],
                    [data_id, "nm", data_config.version]]
    floyd_logger.info(tabulate(table_output, headers="firstrow"))


def abort_previous_upload(data_config):
    try:
        os.remove(data_config.tarball_path)
    except (OSError, TypeError):
        pass

    data_config.set_tarball_path("")
    data_config.set_data_endpoint("")
    DataConfigManager.set_config(data_config)
