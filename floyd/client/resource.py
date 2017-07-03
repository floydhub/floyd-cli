from time import sleep
from floyd.model.resource import Resource
from floyd.log import logger as floyd_logger
from floyd.exceptions import FloydException
from floyd.client.base import FloydHttpClient


class ResourceClient(FloydHttpClient):
    """
    Client to interact with Resource api
    """
    URL_PREFIX = '/resources/'
    WAIT_INTERVAL = 10  # in seconds
    MAX_WAIT_RETRY = 60

    def __init__(self):
        super(ResourceClient, self).__init__()

    def get(self, resource_id):
        try:
            response = self.request('GET', self.URL_PREFIX + resource_id)
            resource_dict = response.json()
            return Resource.from_dict(resource_dict)
        except FloydException as e:
            floyd_logger.info("Resource %s: ERROR! %s", resource_id, e.message)
            return None

    def wait_for_ready(self, resource_id):
        sleep(2)  # initial wait of 2 seconds
        ready = False
        retry_count = 0
        while retry_count < self.MAX_WAIT_RETRY:
            response = self.request('GET', self.URL_PREFIX + resource_id)
            resource_dict = response.json()
            ready = resource_dict['state'] == 'valid'
            if ready:
                break
            retry_count += 1
            yield retry_count
            sleep(self.WAIT_INTERVAL)
        yield retry_count
