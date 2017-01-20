from marshmallow import Schema, fields, post_load

from floyd.constants import TENSORFLOW_DOCKER_IMAGE
from floyd.model.base import BaseModel


class ModuleSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    command = fields.Str()
    module_type = fields.Str()
    default_container = fields.Str()
    family_id = fields.Str(allow_none=True)
    version = fields.Integer(allow_none=True)
    outputs = fields.List(fields.Dict)

    @post_load
    def make_module(self, data):
        return Module(**data)


class Module(BaseModel):
    schema = ModuleSchema(strict=True)
    default_outputs = [{'name': 'output', 'type': 'dir'}]

    def __init__(self,
                 name,
                 description,
                 command,
                 module_type="code",
                 default_container=TENSORFLOW_DOCKER_IMAGE,
                 family_id=None,
                 version=None,
                 outputs=default_outputs):
        self.name = name
        self.description = description
        self.command = command
        self.module_type = module_type
        self.default_container = default_container
        self.family_id = family_id
        self.version = version
        self.outputs = outputs
