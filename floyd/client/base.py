import requests
import os
import sys
import tarfile

import floyd
from floyd.manager.auth_config import AuthConfigManager
from floyd.exceptions import (AuthenticationException, AuthorizationException,
                              BadGatewayException, BadRequestException,
                              FloydException, GatewayTimeoutException,
                              NotFoundException, OverLimitException,
                              ServerException)

from floyd.log import logger as floyd_logger


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
                files=None,
                json=None,
                timeout=5,
                headers=None):
        """
        Execute the request using requests library
        """
        request_url = self.base_url + url
        floyd_logger.debug("Starting request to url: {} with params: {}, data: {}".format(request_url, params, data))

        # Auth headers if access_token is present
        request_headers = {"Authorization": "Bearer {}".format(
            self.access_token.token if self.access_token else None),
        }
        # Add any additional headers
        if headers:
            request_headers.update(headers)

        try:
            response = requests.request(method,
                                        request_url,
                                        params=params,
                                        data=data,
                                        json=json,
                                        headers=request_headers,
                                        files=files,
                                        timeout=timeout)
        except requests.exceptions.ConnectionError as exception:
            floyd_logger.debug("Exception: {}".format(exception))
            sys.exit("Cannot connect to the Floyd server. Check your internet connection.")

        try:
            floyd_logger.debug("Response Content: {}, Headers: {}".format(
                response.json(), response.headers))
        except Exception:
            floyd_logger.debug("Request failed. Response: {}".format(response.content))

        self.check_response_status(response)
        return response

    def download(self, url, filename, relative=False, headers=None, timeout=5):
        """
        Download the file from the given url at the current path
        """
        request_url = self.base_url + url if relative else url
        floyd_logger.debug("Downloading file from url: {}".format(request_url))

        # Auth headers if access_token is present
        request_headers = {"Authorization": "Bearer {}".format(
            self.access_token.token if self.access_token else None),
        }
        # Add any additional headers
        if headers:
            request_headers.update(headers)

        try:
            response = requests.get(request_url,
                                    headers=request_headers,
                                    timeout=timeout,
                                    stream=True)
            self.check_response_status(response)
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return filename
        except requests.exceptions.ConnectionError as exception:
            floyd_logger.debug("Exception: {}".format(exception))
            sys.exit("Cannot connect to the Floyd server. Check your internet connection.")

    def download_tar(self, url, untar=True, delete_after_untar=False):
        """
        Download and optionally untar the tar file from the given url
        """
        try:
            floyd_logger.info("Downloading the tar file to the current directory ...")
            filename = self.download(url=url, filename='output.tar')
            if filename and untar:
                floyd_logger.info("Untarring the contents of the file ...")
                tar = tarfile.open(filename)
                tar.extractall()
                tar.close()
            if delete_after_untar:
                floyd_logger.info("Cleaning up the tar file ...")
                os.remove(filename)
            return filename
        except FloydException as e:
            floyd_logger.info("Download URL ERROR! {}".format(e.message))
            return False

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
            if response.status_code == 400:
                raise BadRequestException(response)
            elif response.status_code == 401:
                raise AuthenticationException()
            elif response.status_code == 403:
                raise AuthorizationException()
            elif response.status_code == 404:
                raise NotFoundException()
            elif response.status_code == 429:
                raise OverLimitException(response.json().get("message"))
            elif response.status_code == 502:
                raise BadGatewayException()
            elif response.status_code == 504:
                raise GatewayTimeoutException()
            elif 500 <= response.status_code < 600:
                if 'Server under maintenance' in response.content.decode():
                    raise ServerException('Server under maintenance, please try again later.')
                else:
                    raise ServerException()
            else:
                msg = "An error occurred. Server response: {}".format(response.status_code)
                raise FloydException(message=msg)
