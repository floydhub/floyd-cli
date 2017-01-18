from floyd.client.base import FloydHttpClient
from floyd.model.experiment import Experiment


class PsClient(FloydHttpClient):
    """
    Check status of experiments / runs
    """
    def __init__(self):
        self.url = "/experiments/"
        super(PsClient, self).__init__()

    def get_all(self):
        response = self.request("GET",
                                self.url)
        experiments_dict = response.json()
        experiments = [Experiment.from_dict(expt) for expt in experiments_dict]
        return experiments

    def get(self, id):
        response = self.request("GET",
                                "{}{}".format(self.url, id))
        experiment_dict = response.json()
        experiment = Experiment.from_dict(experiment_dict)
        return experiment
