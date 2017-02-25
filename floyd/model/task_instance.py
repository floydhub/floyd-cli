from marshmallow import Schema, fields, post_load

from floyd.model.base import BaseModel


class TaskInstanceSchema(Schema):
    id = fields.Str()
    log_id = fields.Str()
    output_ids = fields.Dict(load_from='output_ids_dict')
    mode = fields.Str(allow_none=True)
    module_id = fields.Str(allow_none=True)

    @post_load
    def make_task_instance(self, data):
        return TaskInstance(**data)


class TaskInstance(BaseModel):
    schema = TaskInstanceSchema(strict=True)

    def __init__(self,
                 id,
                 log_id,
                 output_ids,
                 mode,
                 module_id=None):
        self.id = id
        self.log_id = log_id
        self.output_ids = output_ids
        self.mode = mode
        self.module_id = module_id
