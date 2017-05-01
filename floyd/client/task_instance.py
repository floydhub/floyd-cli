from floyd.client.base import FloydHttpClient
from floyd.model.task_instance import TaskInstance
from floyd.exceptions import FloydException
from floyd.log import logger as floyd_logger


class TaskInstanceClient(FloydHttpClient):
    """
    Client to interact with TaskInstance api
    """
    def __init__(self):
        self.url = "/taskinstances/"
        super(TaskInstanceClient, self).__init__()

    def get(self, id):
        try:
            response = self.request("GET",
                                    "{}{}".format(self.url, id))
            task_instance_dict = response.json()
            ti = TaskInstance.from_dict(task_instance_dict)
            return ti
        except FloydException as e:
            floyd_logger.info("Task Instance {}: ERROR! {}".format(id, e.message))
            return None
