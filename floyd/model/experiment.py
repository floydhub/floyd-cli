from marshmallow import Schema, fields, post_load

from floyd.model.base import BaseModel


class ExperimentSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    created = fields.DateTime()
    state = fields.Str()
    duration = fields.Number()

    @post_load
    def make_experiment(self, data):
        return Experiment(**data)


class Experiment(BaseModel):
    schema = ExperimentSchema()

    def __init__(self,
                 id,
                 name,
                 created,
                 state,
                 duration):
        self.id = id
        self.name = name
        self.created = created
        self.state = state
        self.duration = duration
