import click
import os
import sys
from tabulate import tabulate
import tempfile

from floyd.client.data import DataClient
from floyd.client.files import create_tarfile, sizeof_fmt
from floyd.client.tus_data import initialize_upload, resume_upload
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
    data_id = DataClient().create(data) or sys.exit(1)

    # Create tarball of the data using the ID returned from the API
    temp_dir = tempfile.mkdtemp()
    tarball_path = os.path.join(temp_dir, "{}.data.tar.gz".format(data_id))

    floyd_logger.debug("Creating tarfile with contents of current directory: {}".format(tarball_path))
    floyd_logger.info("Compressing data...")

    create_tarfile(source_dir='.', filename=tarball_path)

    data_endpoint = initialize_upload(tarball_path)
    data_config.set_tarball_path(tarball_path)
    data_config.set_data_endpoint(data_endpoint)
    data_config.set_data_predecessor(data_id)

    DataConfigManager.set_config(data_config)

def complete_upload(data_config, access_token):
    data_endpoint = data_config.data_endpoint
    path = data_config.tarball_path
    file_size = os.path.getsize(path)

    floyd_logger.info("Uploading compressed data. Total upload size: {}".format(sizeof_fmt(file_size)))

    resume_upload(path, data_endpoint)

    try:
        os.remove(path)
    except OSError:
        pass

    data_id = data_config.data_predecessor
    floyd_logger.debug("Created data with id : {}".format(data_id))
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

