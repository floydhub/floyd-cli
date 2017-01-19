import json
import os

from floyd.client.base import FloydHttpClient
from floyd.logging import logger as floyd_logger


class ModuleClient(FloydHttpClient):
    """
    Client to interact with Experiments api
    """
    def __init__(self):
        self.url = "/modules/"
        super(ModuleClient, self).__init__()

    def create(self, module):
        upload_files = self.get_local_files()
        request_data = {"json": json.dumps(module.to_dict())}
        floyd_logger.debug("Creating module. Uploading {} files ...".format(len(upload_files)))
        response = self.request("POST",
                                self.url,
                                data=request_data,
                                files=upload_files)
        return response.json().get("id")

    def get_local_files(self):
        local_files = []
        for root, dirs, files in os.walk('.'):
            for file_name in files:
                file_relative_path = os.path.join(root, file_name)
                file_full_path = os.path.join(os.getcwd(), root, file_name)
                local_files.append(('code', (file_relative_path, open(file_full_path, 'rb'), 'text/plain')))

        return local_files
