from marshmallow import Schema, fields, post_load

from floyd.model.base import BaseModel


class ExperimentConfigSchema(Schema):

    name = fields.Str()
    version = fields.Integer()

    @post_load
    def make_access_token(self, data):
        return ExperimentConfig(**data)


class ExperimentConfig(BaseModel):

    schema = ExperimentConfigSchema()

    def __init__(self,
                 name,
                 version=1):
        self.name = name
        self.version = version
