import json
import os

from floyd.client.base import FloydHttpClient
from floyd.config import FloydIgnoreManager
from floyd.log import logger as floyd_logger


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
        floyd_logger.info("Creating module. Uploading {} files ...".format(len(upload_files)))
        response = self.request("POST",
                                self.url,
                                data=request_data,
                                files=upload_files)
        return response.json().get("id")

    def get_local_files(self):
        local_files = []
        ignore_list = FloydIgnoreManager.get_list()
        ignore_list_localized = ["./{}".format(item) for item in ignore_list]
        floyd_logger.debug("Ignoring list : {}".format(ignore_list_localized))

        for root, dirs, files in os.walk('.'):
            ignore_dir = False
            for item in ignore_list_localized:
                if root.startswith(item):
                    ignore_dir = True

            if ignore_dir:
                floyd_logger.debug("Ignoring directory : {}".format(root))
                continue

            for file_name in files:
                file_relative_path = os.path.join(root, file_name)
                file_full_path = os.path.join(os.getcwd(), root, file_name)
                local_files.append(('code', (file_relative_path, open(file_full_path, 'rb'), 'text/plain')))

        return local_files
