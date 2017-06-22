from marshmallow import Schema, fields, post_load

from floyd.model.base import BaseModel


class EnvSchema(Schema):
    arch = fields.Str()
    name = fields.Str()
    image = fields.Str()

    @post_load
    def make_env(self, data):
        return Env(**data)


class Env(BaseModel):
    schema = EnvSchema(strict=True)

    def __init__(self,
                 arch,
                 name,
                 image):
        self.name = name
        self.image = image
        self.arch = arch
