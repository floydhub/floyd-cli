import sys
from floyd.manager.auth_config import AuthConfigManager
from floyd.client.base import FloydHttpClient
from floyd.exceptions import (
    FloydException, AuthenticationException, NotFoundException
)
from floyd.model.dataset import Dataset
from floyd.log import logger as floyd_logger


class DatasetClient(FloydHttpClient):
    """
    Client to get datasets from the server
    """
    def __init__(self):
        self.url = "/datasets"
        super(DatasetClient, self).__init__()

    def get_datasets(self):
        try:
            response = self.request("GET", self.url)
            datasets_dict = response.json()
            return [Dataset.from_dict(dataset) for dataset in datasets_dict.get("datasets", [])]
        except FloydException as e:
            if isinstance(e, AuthenticationException):
                # exit now since there is nothing we can do without login
                sys.exit(1)
            floyd_logger.info("Error while retrieving datasets: {}".format(e.message))
            return []

    def get_by_name(self, name):
        access_token = AuthConfigManager.get_access_token()
        try:
            response = self.request('GET', '%s/%s/%s' % (self.url, access_token.username, name))
            return Dataset.from_dict(response.json())
        except NotFoundException:
            return None
