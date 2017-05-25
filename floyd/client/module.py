import json
import sys
from clint.textui.progress import Bar as ProgressBar

from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from floyd.client.base import FloydHttpClient
from floyd.client.files import get_files_in_current_directory
from floyd.exceptions import FloydException
from floyd.log import logger as floyd_logger


def create_progress_callback(encoder):
    encoder_len = encoder.len
    bar = ProgressBar(expected_size=encoder_len, filled_char='=')

    def callback(monitor):
        bar.show(monitor.bytes_read)
    return callback


class ModuleClient(FloydHttpClient):
    """
    Client to interact with modules api
    """
    def __init__(self):
        self.url = "/modules/"
        super(ModuleClient, self).__init__()

    def create(self, module):
        try:
            upload_files, total_file_size = get_files_in_current_directory(file_type='code')
        except OSError:
            sys.exit("Directory contains too many files to upload. Add unused files and directories to .floydignore file."
                     "Or upload data separately using floyd data command")

        floyd_logger.info("Creating project run. Total upload size: {}".format(total_file_size))
        floyd_logger.debug("Creating module. Uploading: {} files".format(len(upload_files)))
        floyd_logger.info("Syncing code ...")

        # Add request data
        upload_files.append(("json", json.dumps(module.to_dict())))
        multipart_encoder = MultipartEncoder(
            fields=upload_files
        )

        # Attach progress bar
        progress_callback = create_progress_callback(multipart_encoder)
        multipart_encoder_monitor = MultipartEncoderMonitor(multipart_encoder, progress_callback)

        response = self.request("POST",
                                self.url,
                                data=multipart_encoder_monitor,
                                headers={"Content-Type": multipart_encoder.content_type},
                                timeout=3600)

        floyd_logger.info("Done")
        return response.json().get("id")

    def delete(self, id):
        try:
            self.request("DELETE",
                         "{}{}".format(self.url, id))
            return True
        except FloydException as e:
            floyd_logger.info("Module {}: ERROR! {}".format(id, e.message))
            return False
