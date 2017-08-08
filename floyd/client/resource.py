from time import sleep
from floyd.model.resource import Resource
from floyd.log import logger as floyd_logger
from floyd.exceptions import FloydException, WaitTimeoutException
from floyd.client.base import FloydHttpClient


class ResourceClient(FloydHttpClient):
    """
    Client to interact with Resource api
    """
    URL_PREFIX = '/resources/'
    WAIT_INTERVAL = 10  # in seconds
    MAX_WAIT_RETRY = 180  # wait up to 30min

    def __init__(self):
        super(ResourceClient, self).__init__()

    def get(self, resource_id):
        try:
            response = self.request('GET', self.URL_PREFIX + resource_id)
            resource_dict = response.json()
            resource = Resource.from_dict(resource_dict)
            return resource
        except FloydException as e:
            floyd_logger.info("Resource %s: ERROR! %s", resource_id, e.message)
            return None

    def get_content(self, resource_id):
        try:
            response = self.request('GET', self.URL_PREFIX + resource_id + "?content=true")
            return response.content.decode(response.encoding)
        except FloydException as e:
            floyd_logger.debug("Resource %s: ERROR! %s", resource_id, e.message)
            return None

    def wait_for_ready(self, resource_id):
        sleep(2)  # initial wait of 2 seconds
        ready = False
        retry_count = 0
        while retry_count < self.MAX_WAIT_RETRY:
            response = self.request(
                'GET', '%s%s/state' % (self.URL_PREFIX, resource_id))
            new_state = response.json()
            ready = new_state == 'valid'
            if ready:
                break
            retry_count += 1
            yield retry_count
            sleep(self.WAIT_INTERVAL)
        if retry_count >= self.MAX_WAIT_RETRY:
            raise WaitTimeoutException()
        yield retry_count
