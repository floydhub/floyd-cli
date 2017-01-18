import requests

import floyd
from floyd.exceptions import AuthenticationException
from floyd.logging import logger as floyd_logger


class FloydHttpClient(object):
    """
    Base client for all HTTP operations
    """
    def __init__(self):
        self.base_url = "{}/api/v1".format(floyd.floyd_host)

    def request(self,
                method,
                url,
                params=None,
                data=None):
        """
        Execute the request using requests library
        """
        request_url = self.base_url + url
        floyd_logger.debug("Starting request to url: {} with params: {}, data: {}".format(request_url, params, data))
        response = requests.request(method, request_url, params=params, json=data)
        floyd_logger.debug("Response Content: {}, Headers: {}".format(response.json(), response.headers))
        self.check_response_status(response)
        return response

    def check_response_status(self, response):
        """
        Check if response is successful. Else raise Exception.
        """
        if not (200 <= response.status_code < 300):
            try:
                message = response.json()["errors"]
            except Exception:
                message = None
            floyd_logger.debug("Error received : status_code: {}, message: {}".format(response.status_code,
                                                                                      message or response.content))

            if response.status_code == 401:
                raise AuthenticationException(message=message, status_code=response.status_code)
            else:
                response.raise_for_status()
