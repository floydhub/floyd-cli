import json
import sys

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
        try:
            upload_files, total_file_size = get_files_in_directory(path='.', file_type='code')
        except OSError:
            sys.exit("Directory contains too many files to upload. Add unused directories to .floydignore file."
                     "Or download data directly from the internet into FloydHub")

        request_data = {"json": json.dumps(module.to_dict())}
        floyd_logger.info("Creating project run. Total upload size: {}".format(total_file_size))
        floyd_logger.debug("Creating module. Uploading: {} files".format(len(upload_files)))
        floyd_logger.info("Syncing code ...")
        response = self.request("POST",
                                self.url,
                                data=request_data,
                                files=upload_files,
                                timeout=3600)
        return response.json().get("id")

    def delete(self, id):
        self.request("DELETE",
                     "{}{}".format(self.url, id))
        return True
