import json
import os

from clint.textui.progress import Bar as ProgressBar
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from floyd.exceptions import FloydException
from floyd.client.base import FloydHttpClient
from floyd.client.files import create_tarfile, sizeof_fmt
from floyd.model.data import Data
from floyd.log import logger as floyd_logger

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory


def create_progress_callback(encoder):
    encoder_len = encoder.len
    bar = ProgressBar(expected_size=encoder_len, filled_char='=')

    def callback(monitor):
        bar.show(monitor.bytes_read)
    return callback


class DataClient(FloydHttpClient):
    """
    Client to interact with Data api
    """
    def __init__(self):
        self.url = "/modules/"  # Data is a subclass of modules
        super(DataClient, self).__init__()

    def create(self, data):
        """
        Create a temporary directory for the tar file that will be removed at the
        end of the operation.
        """
        with TemporaryDirectory() as temp_directory:
            floyd_logger.info("Compressing data ...")
            compressed_file_path = os.path.join(temp_directory, "data.tar.gz")

            # Create tarfile
            floyd_logger.debug("Creating tarfile with contents of current directory: {}".format(compressed_file_path))
            create_tarfile(source_dir='.', filename=compressed_file_path)

            total_file_size = os.path.getsize(compressed_file_path)
            floyd_logger.info("Creating data source. Total upload size: {}".format(sizeof_fmt(total_file_size)))
            floyd_logger.info("Uploading compressed data ...")

            # Add request data
            request_data = []

            with open(compressed_file_path, 'rb') as compressed_file:
                request_data.append(("data", ('data.tar', compressed_file, 'text/plain')))
                request_data.append(("json", json.dumps(data.to_dict())))

                multipart_encoder = MultipartEncoder(
                    fields=request_data
                )

                # Attach progress bar
                progress_callback = create_progress_callback(multipart_encoder)
                multipart_encoder_monitor = MultipartEncoderMonitor(multipart_encoder, progress_callback)

                response = self.request("POST",
                                        self.url,
                                        data=multipart_encoder_monitor,
                                        headers={"Content-Type": multipart_encoder.content_type},
                                        timeout=3600)

            floyd_logger.info("Done")
            return response.json().get("id")

    def get(self, id):
        try:
            response = self.request("GET",
                                    "{}{}".format(self.url, id))
            data_dict = response.json()
            return Data.from_dict(data_dict)
        except FloydException as e:
            floyd_logger.info("Data {}: ERROR! {}".format(id, e.message))
            return None

    def get_all(self):
        try:
            response = self.request("GET",
                                    self.url,
                                    params="module_type=data")
            data_dict = response.json()
            return [Data.from_dict(data) for data in data_dict]
        except FloydException as e:
            floyd_logger.info("Error while retrieving data: {}".format(e.message))
            return []

    def delete(self, id):
        try:
            self.request("DELETE",
                         "{}{}".format(self.url, id, timeout=10))
            floyd_logger.info("Data {}: Deleted".format(id))
            return True
        except FloydException as e:
            floyd_logger.info("Data {}: ERROR! {}".format(id, e.message))
            return False
