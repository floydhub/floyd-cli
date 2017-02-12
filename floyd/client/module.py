import json

from floyd.client.base import FloydHttpClient
from floyd.client.files import get_files_in_directory
from floyd.log import logger as floyd_logger


class ModuleClient(FloydHttpClient):
    """
    Client to interact with modules api
    """
    def __init__(self):
        self.url = "/modules/"
        super(ModuleClient, self).__init__()

    def create(self, module):
        upload_files = get_files_in_directory(path='.', file_type='code')
        request_data = {"json": json.dumps(module.to_dict())}
        floyd_logger.debug("Creating module. Uploading {} files ...".format(len(upload_files)))
        floyd_logger.info("Syncing code ...")
        response = self.request("POST",
                                self.url,
                                data=request_data,
                                files=upload_files,
                                timeout=3600)
        return response.json().get("id")
