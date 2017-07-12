from floyd.client.base import FloydHttpClient
from floyd.exceptions import FloydException
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
            floyd_logger.info("Error while retrieving datasets: {}".format(e.message))
            return []

    def get_dataset_matching_name(self, name):
        datasets = self.get_datasets()
        for dataset in datasets:
            if name == dataset.name:
                return dataset
        return None
