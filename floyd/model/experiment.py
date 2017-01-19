from marshmallow import Schema, fields, post_load

from floyd.model.base import BaseModel


class ExperimentSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    description = fields.Str()
    created = fields.DateTime()
    state = fields.Str(allow_none=True)
    duration = fields.Number(allow_none=True)
    version = fields.Integer()
    log_id = fields.Str(load_from="logId")
    canvas = fields.Dict(load_only=True)
    task_instances = fields.List(fields.Str(), dump_only=True)

    @post_load
    def make_experiment(self, data):
        return Experiment(**data)


class Experiment(BaseModel):
    schema = ExperimentSchema(strict=True)

    def __init__(self,
                 id,
                 name,
                 description,
                 created,
                 state,
                 duration,
                 log_id,
                 canvas=None):
        self.id = id
        self.name = name
        self.description = description
        self.created = created
        self.state = state
        self.duration = duration
        self.log_id = log_id
        if canvas:
            nodes = canvas.get('nodes', {})
            self.task_instances = [nodes[key].get("taskInstanceId") for key in nodes]
        else:
            self.task_instances = []


class ExperimentRequestSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    module_id = fields.Str()
    family_id = fields.Str(allow_none=True)
    version = fields.Integer(allow_none=True)
    predecessor = fields.Str(allow_none=True)

    @post_load
    def make_experiment_request(self, data):
        return ExperimentRequest(**data)


class ExperimentRequest(BaseModel):
    schema = ExperimentRequestSchema(strict=True)

    def __init__(self,
                 name,
                 description,
                 module_id,
                 predecessor=None,
                 family_id=None,
                 version=None):
        self.name = name
        self.description = description
        self.module_id = module_id
        self.family_id = family_id
        self.version = version
