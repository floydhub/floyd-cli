import json

from floyd.client.base import FloydHttpClient
from floyd.manager.experiment_config import ExperimentConfigManager
from floyd.model.experiment import Experiment


class ExperimentClient(FloydHttpClient):
    """
    Client to interact with Experiments api
    """
    def __init__(self):
        self.url = "/experiments/"
        super(ExperimentClient, self).__init__()

    def get_all(self):
        experiment_config = ExperimentConfigManager.get_config()
        response = self.request("GET",
                                self.url,
                                params="family_id={}".format(experiment_config.family_id))
        experiments_dict = response.json()
        return [Experiment.from_dict(expt) for expt in experiments_dict]

    def get(self, id):
        response = self.request("GET",
                                "{}{}".format(self.url, id))
        experiment_dict = response.json()
        return Experiment.from_dict(experiment_dict)

    def stop(self, id):
        self.request("GET",
                     "{}cancel/{}".format(self.url, id))
        return True

    def create(self, experiment_request):
        response = self.request("POST",
                                "{}run_module/".format(self.url),
                                data=json.dumps(experiment_request.to_dict()),
                                timeout=3600)
        return response.json().get("id")

    def delete(self, id):
        self.request("DELETE",
                     "{}{}".format(self.url, id))
        return True
