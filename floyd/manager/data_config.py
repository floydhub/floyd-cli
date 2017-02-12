import json
import os
from marshmallow import Schema, fields, post_load

from floyd.exceptions import FloydException
from floyd.model.base import BaseModel
from floyd.log import logger as floyd_logger


class DataConfigSchema(Schema):

    name = fields.Str()
    version = fields.Integer()
    family_id = fields.Str()
    data_predecessor = fields.Str(allow_none=True)

    @post_load
    def make_access_token(self, data):
        return DataConfig(**data)


class DataConfig(BaseModel):

    schema = DataConfigSchema(strict=True)

    def __init__(self,
                 name,
                 version=1,
                 family_id=None,
                 data_predecessor=None):
        self.name = name
        self.version = version
        self.family_id = family_id
        self.data_predecessor = data_predecessor

    def increment_version(self):
        self.version = self.version + 1

    def set_data_predecessor(self, data_predecessor):
        self.data_predecessor = data_predecessor


class DataConfigManager(object):
    """
    Manages .floyddata file in the current directory
    """

    CONFIG_FILE_PATH = os.path.join(os.getcwd() + "/.floyddata")

    @classmethod
    def set_config(cls, data_config):
        floyd_logger.debug("Setting {} in the file {}".format(data_config.to_dict(),
                                                              cls.CONFIG_FILE_PATH))
        with open(cls.CONFIG_FILE_PATH, "w") as config_file:
            config_file.write(json.dumps(data_config.to_dict()))

    @classmethod
    def get_config(cls):
        if not os.path.isfile(cls.CONFIG_FILE_PATH):
            raise FloydException("Missing .floyddata file, run floyd data init first")

        with open(cls.CONFIG_FILE_PATH, "r") as config_file:
            data_config_str = config_file.read()
        return DataConfig.from_dict(json.loads(data_config_str))
