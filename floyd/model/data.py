from marshmallow import Schema, fields, post_load

from floyd.model.base import BaseModel


class DataSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    module_type = fields.Str()
    data_type = fields.Str()
    version = fields.Integer(allow_none=True)

    @post_load
    def make_data(self, data):
        return Data(**data)


class Data(BaseModel):
    schema = DataSchema(strict=True)
    default_outputs = [{'name': 'output', 'type': 'dir'}]

    def __init__(self,
                 name,
                 description,
                 module_type="data",
                 data_type="dir",
                 version=None):
        self.name = name
        self.description = description
        self.module_type = module_type
        self.data_type = data_type
        self.version = version
