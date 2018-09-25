import click
import os
import sys
from tabulate import tabulate
import tempfile
from shutil import rmtree
from clint.textui.progress import dots, STREAM as clint_STREAM

from floyd.exceptions import WaitTimeoutException
from floyd.client.data import DataClient
from floyd.client.resource import ResourceClient
from floyd.client.files import create_tarfile, sizeof_fmt
from floyd.client.tus_data import TusDataClient
from floyd.log import logger as floyd_logger
from floyd.manager.data_config import DataConfigManager
from floyd.model.data import DataRequest
from floyd.cli.utils import normalize_data_name


MAX_UPLOAD_SIZE = 1024 * 1024 * 1024 * 100  # bytes = 100 GiB


class ResourceWaitIter(object):
    def __init__(self, resource_id):
        self.resource_id = resource_id

    def __iter__(self):
        for c in ResourceClient().wait_for_ready(self.resource_id):
            yield c

    def __len__(self):
        return ResourceClient.MAX_WAIT_RETRY


def opt_to_resume(resume_flag):
    if resume_flag:
        return True

    msg = "An unfinished upload exists. Would you like to resume it?"
    return click.confirm(msg, abort=False, default=False)


def upload_is_resumable(data_config):
    # TODO: Check to make sure server says the upload is resumable
    return (
        (data_config.resource_id or "") or
        (os.path.isfile(data_config.tarball_path or "") and
         data_config.data_endpoint)
    )


def initialize_new_upload(data_config, access_token, description=None):
    # TODO: hit upload server to check for liveness before moving on
    data_config.set_tarball_path(None)
    data_config.set_data_endpoint(None)
    data_config.set_resource_id(None)

    namespace = data_config.namespace or access_token.username
    data_name = "{}/{}".format(namespace, data_config.name)

    # Create tarball of the data using the ID returned from the API
    # TODO: allow to the users to change directory for the compression
    temp_dir = tempfile.mkdtemp()
    tarball_path = os.path.join(temp_dir, "floydhub_data.tar.gz")

    floyd_logger.debug("Creating tarfile with contents of current directory: %s",
                       tarball_path)
    floyd_logger.info("Compressing data...")
    create_tarfile(source_dir='.', filename=tarball_path)

    # If starting a new upload fails for some reason down the line, we don't
    # want to re-tar, so save off the tarball path now
    data_config.set_tarball_path(tarball_path)
    DataConfigManager.set_config(data_config)

    # Create data object using API
    data = DataRequest(name=data_name,
                       description=description,
                       family_id=data_config.family_id,
                       data_type='gzip')
    data_info = DataClient().create(data)
    if not data_info:
        rmtree(temp_dir)
        sys.exit(1)

    data_config.set_data_id(data_info['id'])
    data_config.set_data_name(data_info['name'])
    DataConfigManager.set_config(data_config)

    # fetch auth token for upload server
    creds = DataClient().new_tus_credentials(data_info['id'])
    if not creds:
        # TODO: delete module from server?
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
    data_id = data_config.data_id
    tarball_path = data_config.tarball_path

    if not data_id:
        floyd_logger.error("Corrupted upload state, please start a new one.")
        sys.exit(1)

    # check for tarball upload, upload to server if not done
    if not data_config.resource_id and (tarball_path and data_endpoint):
        floyd_logger.debug("Getting fresh upload credentials")
        creds = DataClient().new_tus_credentials(data_id)
        if not creds:
            sys.exit(1)

        file_size = os.path.getsize(tarball_path)
        # check for upload limit dimension
        if file_size > MAX_UPLOAD_SIZE:
            try:
                floyd_logger.info("Removing compressed data...")
                rmtree(os.path.dirname(tarball_path))
            except (OSError, TypeError):
                pass

            sys.exit(("Data size too large to upload, please keep it under %s.\n") %
                     (sizeof_fmt(MAX_UPLOAD_SIZE)))

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

        floyd_logger.debug("Created data with id : %s", data_id)
        floyd_logger.info("Upload finished.")

        # Update data config
        data_config.set_tarball_path(None)
        data_config.set_data_endpoint(None)
        data_source = DataClient().get(data_id)
        data_config.set_resource_id(data_source.resource_id)
        DataConfigManager.set_config(data_config)

    # data tarball uploaded, check for server untar
    if data_config.resource_id:
        floyd_logger.info(
            "Waiting for server to unpack data.\n"
            "You can exit at any time and come back to check the status with:\n"
            "\tfloyd data upload -r")
        try:
            for i in dots(ResourceWaitIter(data_config.resource_id),
                          label='Waiting for unpack...'):
                pass
        except WaitTimeoutException:
            clint_STREAM.write('\n')
            clint_STREAM.flush()
            floyd_logger.info(
                "Looks like it is going to take longer for Floydhub to unpack "
                "your data. Please check back later.")
            sys.exit(1)
        else:
            data_config.set_resource_id(None)
            data_config.set_tarball_path(None)
            data_config.set_data_endpoint(None)
            data_config.set_resource_id(None)
            data_config.set_data_id(None)
            DataConfigManager.set_config(data_config)

    # Print output
    table_output = [["NAME"],
                    [normalize_data_name(data_config.data_name)]]
    floyd_logger.info('')
    floyd_logger.info(tabulate(table_output, headers="firstrow"))


def abort_previous_upload(data_config):
    if data_config.tarball_path and os.path.exists(data_config.tarball_path):
        rmtree(os.path.dirname(data_config.tarball_path))

    data_config.set_tarball_path("")
    data_config.set_data_endpoint("")
    DataConfigManager.set_config(data_config)
