from __future__ import print_function
import base64
from clint.textui.progress import Bar as ProgressBar
import os
import requests

import floyd
from floyd.exceptions import FloydException, LockedException
from floyd.client.base import FloydHttpClient
from floyd.log import logger as floyd_logger


class TusDataClient(FloydHttpClient):
    """
    Client to interact with Data api
    """
    DEFAULT_CHUNK_SIZE = 5 * 1024 * 1024  # 5MB
    TUS_VERSION = '1.0.0'

    def __init__(self, chunk_size=None, base_url=None):
        super(TusDataClient, self).__init__()
        self.chunk_size = chunk_size or self.DEFAULT_CHUNK_SIZE
        self.base_url = base_url or floyd.tus_server_endpoint

    def initialize_upload(self,
                          file_path,
                          base_url=None,
                          headers=None,
                          metadata=None,
                          auth=None):
        base_url = base_url or self.base_url
        floyd_logger.info("Initializing upload...")

        file_size = os.path.getsize(file_path)

        h = {
            "Tus-Resumable": self.TUS_VERSION,
            "Upload-Length": str(file_size),
        }

        if headers:
            h.update(headers)

        if metadata:
            pairs = [
                k + ' ' + base64.b64encode(v.encode('utf-8')).decode()
                for k, v in metadata.items()
            ]
            h["Upload-Metadata"] = ','.join(pairs)

        try:
            response = requests.post(base_url, headers=h, auth=auth)
            self.check_response_status(response)

            location = response.headers["Location"]
            floyd_logger.debug("Data upload endpoint: %s", location)
        except FloydException as e:
            floyd_logger.info("Data upload create: ERROR! %s", e.message)
            location = ""
        except requests.exceptions.ConnectionError as e:
            floyd_logger.error(
                "Cannot connect to the Floyd data upload server for upload url. "
                "Check your internet connection.")
            location = ""

        return location

    def resume_upload(self,
                      file_path,
                      file_endpoint,
                      chunk_size=None,
                      headers=None,
                      auth=None,
                      offset=None):
        chunk_size = chunk_size or self.chunk_size

        try:
            offset = self._get_offset(file_endpoint, headers=headers, auth=auth)
        except LockedException:
            floyd_logger.error("Server busy handling last uploaded part, please wait and try again later.")
            return False
        except FloydException as e:
            floyd_logger.error(
                "Failed to fetch offset data from upload server! %s",
                e.message)
            return False
        except requests.exceptions.ConnectionError as e:
            floyd_logger.error(
                "Cannot connect to the Floyd data upload server for offset. "
                "Check your internet connection.")
            return False

        total_sent = 0
        file_size = os.path.getsize(file_path)

        with open(file_path, 'rb') as f:

            pb = ProgressBar(filled_char="=", expected_size=file_size)
            while offset < file_size:
                pb.show(offset)
                f.seek(offset)
                data = f.read(chunk_size)
                try:
                    offset = self._upload_chunk(data, offset, file_endpoint, headers=headers, auth=auth)
                    total_sent += len(data)
                    floyd_logger.debug("%s bytes sent", total_sent)
                except FloydException as e:
                    floyd_logger.error(
                        "Failed to fetch offset data from upload server! %s",
                        e.message)
                    return False
                except requests.exceptions.ConnectionError as e:
                    floyd_logger.error(
                        "Cannot connect to the Floyd data upload server. "
                        "Check your internet connection.")
                    return False

            # Complete the progress bar with one more call to show()
            pb.show(offset)
            pb.done()
        return True

    def _get_offset(self, file_endpoint, headers=None, auth=None):
        floyd_logger.debug("Getting offset")

        h = {"Tus-Resumable": self.TUS_VERSION}

        if headers:
            h.update(headers)

        response = requests.head(file_endpoint, headers=h, auth=auth)
        self.check_response_status(response)

        offset = int(response.headers["Upload-Offset"])
        floyd_logger.debug("offset: %s", offset)
        return offset

    def _upload_chunk(self, data, offset, file_endpoint, headers=None, auth=None):
        floyd_logger.debug("Uploading %s bytes chunk from offset: %s", len(data), offset)

        h = {
            'Content-Type': 'application/offset+octet-stream',
            'Upload-Offset': str(offset),
            'Tus-Resumable': self.TUS_VERSION,
        }

        if headers:
            h.update(headers)

        response = requests.patch(file_endpoint, headers=h, data=data, auth=auth)
        self.check_response_status(response)

        return int(response.headers["Upload-Offset"])
