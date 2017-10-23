from marshmallow import Schema, fields, post_load
from pytz import utc

from floyd.constants import PST_TIMEZONE
from floyd.date_utils import pretty_date
from floyd.model.base import BaseModel


class DataDetailsSchema(Schema):
    state = fields.Str()
    size = fields.Str()

    @post_load
    def make_data_details(self, data_details):
        return DataDetails(**data_details)


class DataDetails(BaseModel):
    schema = DataDetailsSchema(strict=True)

    def __init__(self,
                 state,
                 size):
        self.state = state
        self.size = size


class DataSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    created = fields.DateTime(load_from="date_created")
    description = fields.Str(allow_none=True)
    data = fields.Nested(DataDetailsSchema)
    version = fields.Str(allow_none=True)
    resource_id = fields.Str(allow_none=True)

    @post_load
    def make_data(self, data):
        return Data(**data)


class Data(BaseModel):
    schema = DataSchema(strict=True)

    def __init__(self,
                 id,
                 name,
                 created,
                 description,
                 data,
                 version=None,
                 resource_id=None):
        self.id = id
        self.name = name
        self.created = self.localize_date(created)
        self.description = description
        self.size = data.size
        self.state = data.state
        self.version = int(float(version)) if version else None
        self.resource_id = resource_id

    def localize_date(self, date):
        if not date.tzinfo:
            date = utc.localize(date)
        return date.astimezone(PST_TIMEZONE)

    @property
    def created_pretty(self):
        return pretty_date(self.created)


class DataRequestSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    module_type = fields.Str()
    data_type = fields.Str()
    version = fields.Integer(allow_none=True)
    family_id = fields.Str(allow_none=True)

    @post_load
    def make_data(self, data):
        return Data(**data)


class DataRequest(BaseModel):
    schema = DataRequestSchema(strict=True)

    def __init__(self,
                 name,
                 description=None,
                 module_type="data",
                 data_type="dir",
                 family_id=None,
                 version=None):
        self.name = name
        self.description = description
        self.module_type = module_type
        self.data_type = data_type
        self.family_id = family_id
        self.version = version
