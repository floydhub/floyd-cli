from floyd.exceptions import FloydException
from floyd.client.base import FloydHttpClient
from floyd.log import logger as floyd_logger


class EnvClient(FloydHttpClient):
    """
    Client to interact with Env api
    """
    def __init__(self):
        self.url = "/env"
        super(EnvClient, self).__init__()

    def get_all(self):
        try:
            response = self.request("GET",
                                    self.url)
            return response.json()
        except FloydException as e:
            floyd_logger.info("Error while retrieving env: {}".format(e.message))
            return {}
