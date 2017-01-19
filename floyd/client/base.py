import requests
from json.decoder import JSONDecodeError

import floyd
from floyd.config import AuthConfigManager
from floyd.exceptions import AuthenticationException, NotFoundException
from floyd.logging import logger as floyd_logger


class FloydHttpClient(object):
    """
    Base client for all HTTP operations
    """
    def __init__(self):
        self.base_url = "{}/api/v1".format(floyd.floyd_host)
        self.access_token = AuthConfigManager.get_access_token()

    def request(self,
                method,
                url,
                params=None,
                data=None,
                files=None):
        """
        Execute the request using requests library
        """
        request_url = self.base_url + url
        floyd_logger.debug("Starting request to url: {} with params: {}, data: {}".format(request_url, params, data))

        response = requests.request(method,
                                    request_url,
                                    params=params,
                                    headers={"Authorization": "Bearer {}".format(
                                        self.access_token.token if self.access_token else None)
                                    },
                                    data=data,
                                    files=files)

        try:
            floyd_logger.debug("Response Content: {}, Headers: {}".format(response.json(), response.headers))
        except JSONDecodeError:
            floyd_logger.error("Request failed. Response: {}".format(response.content))

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
                raise AuthenticationException()
            elif response.status_code == 404:
                raise NotFoundException()
            else:
                response.raise_for_status()
