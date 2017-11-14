from marshmallow import Schema, fields, post_load

from floyd.model.base import BaseModel


class ExperimentConfigSchema(Schema):

    name = fields.Str()
    family_id = fields.Str()

    @post_load
    def make_access_token(self, data):
        return ExperimentConfig(**data)


class ExperimentConfig(BaseModel):

    schema = ExperimentConfigSchema(strict=True)

    def __init__(self,
                 name,
                 family_id=None):
        self.name = name
        self.family_id = family_id
