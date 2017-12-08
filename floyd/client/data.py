from clint.textui.progress import Bar as ProgressBar

from floyd.manager.auth_config import AuthConfigManager
from floyd.exceptions import FloydException, BadRequestException
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
        Create a temporary directory for the tar file that will be removed at
        the end of the operation.
        """
        try:
            floyd_logger.info("Making create request to server...")
            post_body = data.to_dict()
            post_body["resumable"] = True
            response = self.request("POST", self.url, json=post_body)
            return response.json()
        except BadRequestException as e:
            if 'Dataset not found, ID' in e.message:
                floyd_logger.error(
                    'Data create: ERROR! Please run "floyd data init DATASET_NAME" before upload.')
            else:
                floyd_logger.error('Data create: ERROR! %s', e.message)
            return None
        except FloydException as e:
            floyd_logger.error("Data create: ERROR! %s", e.message)
            return None

    def new_tus_credentials(self, data_id):
        try:
            response = self.request(
                "POST",
                "%s%s/upload_v2_credentials" % (self.url, data_id))
            data_dict = response.json()
            return (data_dict["data_upload_id"], data_dict["token"])
        except FloydException as e:
            floyd_logger.error(
                "Error while fetching data upload metadata for %s:\n\t%s",
                data_id, e.message)
            return ()

    def get(self, id):
        try:
            response = self.request("GET", self.url + id)
            data_dict = response.json()
            if data_dict['module_type'] != 'DataModule':
                floyd_logger.error(
                    "Data %s: ERROR! Resource given is not a data.", id)
                return None

            return Data.from_dict(data_dict)
        except FloydException as e:
            floyd_logger.info("Data %s: ERROR! %s\nIf you have already created the dataset, make sure you have uploaded at least one version.", id, e.message)
            return None

    def get_all(self):
        try:
            access_token = AuthConfigManager.get_access_token()
            response = self.request("GET",
                                    self.url,
                                    params={"module_type": "data",
                                            "username": access_token.username})
            data_dict = response.json()
            return [Data.from_dict(data) for data in data_dict]
        except FloydException as e:
            floyd_logger.error("Error while retrieving data: %s", e.message)
            return []

    def delete(self, data_id):
        try:
            # data delete is a synchronous process, it can take a long time
            self.request("DELETE", self.url + data_id, timeout=60)
            return True
        except FloydException as e:
            floyd_logger.error("Data %s: ERROR! %s", data_id, e.message)
            return False
