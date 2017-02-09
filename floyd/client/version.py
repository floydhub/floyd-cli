from floyd.client.base import FloydHttpClient
from floyd.model.version import CliVersion
from floyd.log import logger as floyd_logger


class VersionClient(FloydHttpClient):
    """
    Client to get API version from the server
    """
    def __init__(self):
        self.url = "/cli_version"
        super(VersionClient, self).__init__()

    def get_cli_version(self):
        response = self.request("GET", self.url)
        data_dict = response.json()
        floyd_logger.debug("CLI Version info :{}".format(data_dict))
        return CliVersion.from_dict(data_dict)
