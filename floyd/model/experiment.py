from marshmallow import Schema, fields, post_load

from floyd.model.base import BaseModel


class ExperimentSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    created = fields.DateTime()
    state = fields.Str()
    duration = fields.Number()
    log_id = fields.Str(load_from="logId")
    canvas = fields.Dict(load_only=True)
    task_instances = fields.List(fields.Str(), dump_only=True)

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
                 duration,
                 log_id,
                 canvas=None):
        self.id = id
        self.name = name
        self.created = created
        self.state = state
        self.duration = duration
        self.log_id = log_id
        if canvas:
            nodes = canvas.get('nodes', {})
            self.task_instances = [nodes[key].get("taskInstanceId") for key in nodes]
        else:
            self.task_instances = []
