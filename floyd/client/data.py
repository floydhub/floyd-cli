import json
import os

from clint.textui.progress import Bar as ProgressBar
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from floyd.exceptions import FloydException
from floyd.client.base import FloydHttpClient
from floyd.model.data import Data
from floyd.log import logger as floyd_logger

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
        try:
            floyd_logger.info("Making create request to server...")
            response = self.request("POST",
                                    self.url,
                                    data={"resumable": "true"})

            floyd_logger.info("Done")
            return response.json().get("id")
        except FloydException as e:
            floyd_logger.info("Data create: ERROR! {}".format(e.message))
            return None

    def new_tus_credentials(self, id):
        try:
            response = self.request("POST",
                                    "{}new_credentials/".format(self.url),
                                    data=json.dumps({"id": id}))
            data_dict = response.json()
            return (data_dict["id"], data_dict["token"])
        except FloydException as e:
            floyd_logger.info("Error while fetching data upload credentials! {}".format(id, e.message))
            return ()

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
