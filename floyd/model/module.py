from marshmallow import Schema, fields, post_load

from floyd.model.base import BaseModel


class ModuleSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    command = fields.Str()
    module_type = fields.Str()
    default_container = fields.Str()

    @post_load
    def make_module(self, data):
        return Module(**data)


class Module(BaseModel):
    schema = ModuleSchema()

    def __init__(self,
                 name,
                 description,
                 command,
                 module_type="code",
                 default_container="tensorflow/tensorflow:0.12.1-py3"):
        self.name = name
        self.description = description
        self.command = command
        self.module_type = module_type
        self.default_container = default_container
