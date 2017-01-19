import json

from floyd.client.base import FloydHttpClient


class ModuleClient(FloydHttpClient):
    """
    Client to interact with Experiments api
    """
    def __init__(self):
        self.url = "/modules/"
        super(ModuleClient, self).__init__()

    def create(self, module):
        request_data = {"json": json.dumps(module.to_dict())}
        response = self.request("POST",
                                self.url,
                                data=request_data)
        return response.json().get("id")
