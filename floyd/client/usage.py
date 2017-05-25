import json
import sys

from floyd.client.base import FloydHttpClient
from floyd.client.files import get_files_in_current_directory
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
        try:
            upload_files, total_file_size = get_files_in_current_directory(file_type='data')
        except OSError:
            sys.exit("Directory contains too many files to upload. Add unused files and directories to .floydignore file. "
                     "Or download data directly from the internet into FloydHub")

        request_data = {"json": json.dumps(data.to_dict())}
        floyd_logger.info("Creating data source. Total upload size: {}".format(total_file_size))
        floyd_logger.debug("Total files: {}".format(len(upload_files)))
        floyd_logger.info("Uploading files ...".format(len(upload_files)))
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
