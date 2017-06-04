from __future__ import print_function
import os
import base64
import requests

from floyd.log import logger as floyd_logger

DEFAULT_CHUNK_SIZE = 4 * 1024 * 1024
TUS_VERSION = '1.0.0'
TUS_SERVER_URL = 'http://localhost:8080/uploads/'


def initialize_upload(file_path, headers=None, metadata=None):
    floyd_logger.info("Initializing upload...")

    file_size = os.path.getsize(file_path)

    h = {
        "Tus-Resumable": TUS_VERSION,
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

    response = requests.post(TUS_SERVER_URL, headers=h)
    response.raise_for_status()

    location = response.headers["Location"]
    floyd_logger.debug("Data upload enpoint: {}".format(location))
    return location


def resume_upload(file_path,
                  file_endpoint,
                  chunk_size=DEFAULT_CHUNK_SIZE,
                  headers=None,
                  offset=None):

    offset = _get_offset(file_endpoint, headers=headers)

    total_sent = 0
    file_size = os.path.getsize(file_path)

    with open(file_path, 'rb') as f:
        while offset < file_size:
            f.seek(offset)
            data = f.read(chunk_size)
            offset = _upload_chunk(data, offset, file_endpoint, headers=headers)
            total_sent += len(data)
            floyd_logger.debug("{} bytes sent".format(total_sent))


def _get_offset(file_endpoint, headers=None):
    floyd_logger.debug("Getting offset")

    h = {"Tus-Resumable": TUS_VERSION}

    if headers:
        h.update(headers)

    response = requests.head(file_endpoint, headers=h)
    response.raise_for_status()

    offset = int(response.headers["Upload-Offset"])
    floyd_logger.debug("offset:{}".format(offset))
    return offset


def _upload_chunk(data, offset, file_endpoint, headers=None):
    floyd_logger.debug("Uploading {} bytes chunk from offset: {}".format(len(data), offset))

    h = {
        'Content-Type': 'application/offset+octet-stream',
        'Upload-Offset': str(offset),
        'Tus-Resumable': TUS_VERSION,
    }

    if headers:
        h.update(headers)

    response = requests.patch(file_endpoint, headers=h, data=data)
    if response.status_code != 204:
        raise TusError("Upload chunk failed: Status: {}".format(response.status_code),
                       response=response)

    return int(response.headers["Upload-Offset"])
