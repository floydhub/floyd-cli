import json
import sys
from clint.textui.progress import Bar as ProgressBar

from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from floyd.client.base import FloydHttpClient
from floyd.client.files import get_files_in_current_directory, sizeof_fmt
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

    MAX_UPLOAD_SIZE = 1024 * 1024 * 100

    def __init__(self):
        self.url = "/modules/"
        super(ModuleClient, self).__init__()

    def create(self, module, cli_default=None):
        try:
            upload_files, total_file_size = get_files_in_current_directory(file_type='code')
        except OSError:
            sys.exit("Directory contains too many files to upload. If you have data files in the current directory, "
                     "please upload them separately using \"floyd data\" command and remove them from here.\n"
                     "See http://docs.floydhub.com/faqs/job/#i-get-too-many-open-files-error-when-i-run-my-project "
                     "for more details on how to fix this.")

        if total_file_size > self.MAX_UPLOAD_SIZE:
            sys.exit(("Code size too large to sync, please keep it under %s.\n"
                      "If you have data files in the current directory, please upload them "
                      "separately using \"floyd data\" command and remove them from here.\n"
                      "You may find the following documentation useful:\n\n"
                      "\thttps://docs.floydhub.com/guides/create_and_upload_dataset/\n"
                      "\thttps://docs.floydhub.com/guides/data/mounting_data/\n"
                      "\thttps://docs.floydhub.com/guides/floyd_ignore/") % (sizeof_fmt(self.MAX_UPLOAD_SIZE)))

        floyd_logger.info("Creating project run. Total upload size: %s",
                          sizeof_fmt(total_file_size))
        floyd_logger.debug("Creating module. Uploading: %s files",
                           len(upload_files))
        floyd_logger.info("Syncing code ...")

        # Add request data
        args_payload = module.to_dict()
        if cli_default:
            args_payload['cli_default'] = cli_default
        upload_files.append(("json", json.dumps(args_payload)))
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
