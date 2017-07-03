from marshmallow import Schema, fields
from floyd.model.base import BaseModel


class ResourceSchema(Schema):
    id = fields.Str()
    uri = fields.Str()
    state = fields.Str()
    resource_type = fields.Str()
    size = fields.Str()
    date_finalized = fields.DateTime()
    date_last_updated = fields.DateTime()


class Resource(BaseModel):
    schema = ResourceSchema(strict=True)

    def __init__(self,
                 resource_id,
                 uri,
                 state,
                 resource_type,
                 size,
                 date_finalized,
                 date_last_updated):
        self.id = resource_id
        self.uri = uri
        self.state = state
        self.resource_type = resource_type
        self.size = size
        self.date_finalized = date_finalized
        self.date_last_updated = date_last_updated
