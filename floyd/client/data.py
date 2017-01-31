import json

from floyd.client.base import FloydHttpClient
from floyd.client.files import get_files_in_directory
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
        floyd_logger.info("Creating module. Uploading {} files ...".format(len(upload_files)))
        response = self.request("POST",
                                self.url,
                                data=request_data,
                                files=upload_files)
        return response.json().get("id")
