import json
import os
from marshmallow import Schema, fields, post_load

from floyd.exceptions import FloydException
from floyd.model.base import BaseModel
from floyd.log import logger as floyd_logger


class DataConfigSchema(Schema):

    name = fields.Str()
    family_id = fields.Str()
    namespace = fields.Str(allow_none=True)
    data_id = fields.Str(allow_none=True)
    tarball_path = fields.Str(allow_none=True)
    data_endpoint = fields.Str(allow_none=True)
    resource_id = fields.Str(allow_none=True)
    data_name = fields.Str(allow_none=True)

    @post_load
    def make_access_token(self, data):
        return DataConfig(**data)


class DataConfig(BaseModel):

    schema = DataConfigSchema(strict=True)

    def __init__(self,
                 name,
                 namespace=None,
                 family_id=None,
                 data_id=None,
                 tarball_path=None,
                 data_endpoint=None,
                 resource_id=None,
                 data_name=None):
        self.name = name
        self.namespace = namespace
        self.family_id = family_id
        self.data_id = data_id
        self.tarball_path = tarball_path
        self.data_endpoint = data_endpoint
        self.resource_id = resource_id
        self.data_name = data_name

    def set_data_id(self, data_id):
        self.data_id = data_id

    def set_tarball_path(self, tarball_path):
        self.tarball_path = tarball_path

    def set_data_endpoint(self, data_endpoint):
        self.data_endpoint = data_endpoint

    def set_resource_id(self, resource_id):
        self.resource_id = resource_id

    def set_data_name(self, data_name):
        self.data_name = data_name


class DataConfigManager(object):
    """
    Manages .floyddata file in the current directory
    """

    CONFIG_FILE_PATH = os.path.join(os.getcwd() + "/.floyddata")

    @classmethod
    def set_config(cls, data_config):
        floyd_logger.debug("Setting %s in the file %s", data_config.to_dict(), cls.CONFIG_FILE_PATH)
        with open(cls.CONFIG_FILE_PATH, "w") as config_file:
            config_file.write(json.dumps(data_config.to_dict()))

    @classmethod
    def get_config(cls):
        if not os.path.isfile(cls.CONFIG_FILE_PATH):
            raise FloydException("Missing .floyddata file, run floyd data init first")

        with open(cls.CONFIG_FILE_PATH, "r") as config_file:
            data_config_str = config_file.read()
        return DataConfig.from_dict(json.loads(data_config_str))
