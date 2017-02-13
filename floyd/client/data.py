import json

from floyd.client.base import FloydHttpClient
from floyd.client.files import get_files_in_directory
from floyd.model.data import Data
from floyd.log import logger as floyd_logger


class DataClient(FloydHttpClient):
    """
    Client to interact with Data api
    """
    def __init__(self):
        self.url = "/modules/"  # Data is a subclass of modules
        super(DataClient, self).__init__()

    def create(self, data):
        upload_files = get_files_in_directory(path='.', file_type='data')
        request_data = {"json": json.dumps(data.to_dict())}
        floyd_logger.info("Creating data source. Uploading {} files ...".format(len(upload_files)))
        response = self.request("POST",
                                self.url,
                                data=request_data,
                                files=upload_files,
                                timeout=3600)
        return response.json().get("id")

    def get(self, id):
        response = self.request("GET",
                                "{}{}".format(self.url, id))
        data_dict = response.json()
        return Data.from_dict(data_dict)

    def get_all(self):
        response = self.request("GET",
                                self.url,
                                params="module_type=data")
        experiments_dict = response.json()
        return [Data.from_dict(expt) for expt in experiments_dict]
