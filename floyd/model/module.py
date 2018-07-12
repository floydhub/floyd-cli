from marshmallow import Schema, fields, post_load

from floyd.constants import DEFAULT_DOCKER_IMAGE, DEFAULT_ENV
from floyd.model.base import BaseModel


class ModuleSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    command = fields.Str()
    mode = fields.Str(allow_none=True)
    enable_tensorboard = fields.Boolean()
    module_type = fields.Str()
    # TODO: remove default_container once we fully migrated to env mapping
    default_container = fields.Str(allow_none=True)
    family_id = fields.Str(allow_none=True)
    outputs = fields.List(fields.Dict)
    inputs = fields.List(fields.Dict)
    env = fields.Str()
    # TODO: remove arch, not used by API anymore
    arch = fields.Str(allow_none=True)
    instance_type = fields.Str(allow_none=True)
    resource_id = fields.Str()
    yaml_config = fields.Str()
    task = fields.Str()

    @post_load
    def make_module(self, data):
        return Module(**data)


class Module(BaseModel):
    schema = ModuleSchema(strict=True)

    def __init__(self,
                 name,
                 description,
                 command,
                 mode="cli",
                 enable_tensorboard=False,
                 module_type="code",
                 default_container=DEFAULT_DOCKER_IMAGE,
                 family_id=None,
                 outputs=None,
                 inputs=None,
                 env=DEFAULT_ENV,
                 arch=None,
                 instance_type=None,
                 resource_id=None,
                 yaml_config=None,
                 task=None):
        self.name = name
        self.description = description
        self.command = command
        self.mode = mode
        self.enable_tensorboard = enable_tensorboard
        self.module_type = module_type
        self.default_container = default_container
        self.family_id = family_id
        self.outputs = outputs if outputs else [{'name': 'output', 'type': 'dir'}]
        self.inputs = inputs if inputs else []
        self.env = env
        self.arch = arch
        self.instance_type = instance_type
        self.resource_id = resource_id
        self.yaml_config = yaml_config
        self.task = task
