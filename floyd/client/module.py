import json
import sys
from clint.textui.progress import Bar as ProgressBar

from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from floyd.client.base import FloydHttpClient
from floyd.client.files import get_files_in_current_directory
from floyd.exceptions import FloydException
from floyd.log import logger as floyd_logger
from floyd.model.module import Module


def create_progress_callback(encoder):
    encoder_len = encoder.len
    bar = ProgressBar(expected_size=encoder_len, filled_char='=')

    def callback(monitor):
        bar.show(monitor.bytes_read)

    return callback, bar


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
            sys.exit("Directory contains too many files to upload. If you have data files in the current directory, "
                     "please upload them separately using \"floyd data\" command and remove them from here.\n"
                     "See http://docs.floydhub.com/faqs/job/#i-get-too-many-open-files-error-when-i-run-my-project "
                     "for more details on how to fix this.")

        floyd_logger.info("Creating project run. Total upload size: %s",
                          total_file_size)
        floyd_logger.debug("Creating module. Uploading: %s files",
                           len(upload_files))
        floyd_logger.info("Syncing code ...")

        # Add request data
        upload_files.append(("json", json.dumps(module.to_dict())))
        multipart_encoder = MultipartEncoder(
            fields=upload_files
        )

        # Attach progress bar
        progress_callback, bar = create_progress_callback(multipart_encoder)
        multipart_encoder_monitor = MultipartEncoderMonitor(multipart_encoder, progress_callback)

        try:
            response = self.request("POST",
                                    self.url,
                                    data=multipart_encoder_monitor,
                                    headers={"Content-Type": multipart_encoder.content_type},
                                    timeout=3600)
        finally:
            # always make sure we clear the console
            bar.done()
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

    def get(self, id):
        response = self.request("GET",
                                "{}{}".format(self.url, id))
        module_dict = response.json()
        return Module.from_dict(module_dict)
