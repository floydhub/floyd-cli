import sys
from floyd.manager.auth_config import AuthConfigManager
from floyd.client.base import FloydHttpClient
from floyd.exceptions import (
    FloydException, AuthenticationException, NotFoundException
)
from floyd.model.dataset import Dataset
from floyd.log import logger as floyd_logger
from floyd.manager.data_config import DataConfigManager
from floyd.cli.utils import get_namespace_from_name


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

    def get_by_name(self, name, namespace=None):
        """
        name: can be either <namespace>/<dataset_name> or just <dataset_name>
        namespace: if specified, will skip name parsing, defaults to current user's username
        """
        if not namespace:
            namespace, name = get_namespace_from_name(name)
        if not namespace:
            namespace = AuthConfigManager.get_access_token().username
        try:
            response = self.request('GET', '%s/%s/%s' % (self.url, namespace, name))
            return Dataset.from_dict(response.json())
        except NotFoundException:
            return None

    def add_data(self, source):
        data_config = DataConfigManager.get_config()
        dataset_id = data_config.family_id
        if not dataset_id:
            sys.exit('Please initialize current directory with \'floyd data init DATASET_NAME\' first.')
        re = self.request('POST', '%s/%s' % (self.url, dataset_id), json={'source': source})
        return re.json()
