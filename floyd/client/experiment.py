import json

from floyd.client.base import FloydHttpClient
from floyd.model.experiment import Experiment


class ExperimentClient(FloydHttpClient):
    """
    Client to interact with Experiments api
    """
    def __init__(self):
        self.url = "/experiments/"
        super(ExperimentClient, self).__init__()

    def get_all(self):
        response = self.request("GET",
                                self.url)
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
                                data=json.dumps(experiment_request.to_dict()))
        return response.json().get("id")
