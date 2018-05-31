import json

from floyd.client.base import FloydHttpClient
from floyd.manager.experiment_config import ExperimentConfigManager
from floyd.model.experiment import Experiment
from floyd.exceptions import FloydException, NotFoundException
from floyd.log import logger as floyd_logger


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
        self.request("GET", "{}cancel/{}".format(self.url, id))
        return True

    def restart(self, expt_id, parameters=None):
        if parameters is None:
            parameters = {}
        re = self.request("POST", "{}restart/{}".format(self.url, expt_id), json=parameters)
        return re.json()

    def create(self, experiment_request, cli_default=None):
        payload = experiment_request.to_dict()
        if cli_default:
            payload['cli_default'] = cli_default
        return self.request("POST",
                            self.url + "run_module/",
                            data=json.dumps(payload),
                            timeout=3600).json()

    def delete(self, id):
        try:
            self.request("DELETE",
                         "{}{}".format(self.url, id))
            return True
        except NotFoundException as e:
            floyd_logger.info(
                ("Job {}: ERROR! A deletable job with this "
                 "id was not found. Make sure you have the correct id and "
                 "that the job is not "
                 "queued or running.".format(id))
            )
            return False
        except FloydException as e:
            floyd_logger.info("Job {}: ERROR! {}".format(id, e.message))
            return False
