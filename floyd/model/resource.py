from marshmallow import Schema, fields, post_load
from floyd.model.base import BaseModel


class ResourceSchema(Schema):
    id = fields.Str()
    state = fields.Str(allow_none=True)
    resource_type = fields.Str()
    size = fields.Str()
    date_finalized = fields.DateTime(allow_none=True)
    date_last_updated = fields.DateTime(allow_none=True)

    @post_load
    def make_resource(self, data):
        return Resource(**data)


class Resource(BaseModel):
    schema = ResourceSchema(strict=True)

    def __init__(self,
                 id,
                 state,
                 resource_type,
                 size,
                 date_finalized,
                 date_last_updated):
        self.id = id
        self.state = state
        self.resource_type = resource_type
        self.size = size
        self.date_finalized = date_finalized
        self.date_last_updated = date_last_updated
