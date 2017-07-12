from marshmallow import Schema, fields, post_load

from floyd.model.base import BaseModel


class DatasetSchema(Schema):
    """
    Dataset schema
    """
    name = fields.Str()
    id = fields.Str()
    description = fields.Str(allow_none=True)
    public = fields.Boolean()

    @post_load
    def make_credentials(self, data):
        return Dataset(**data)


class Dataset(BaseModel):
    """
    Latest version is the newest cli available on PIP
    Minimum version is the version below which CLI should fail
    """
    schema = DatasetSchema(strict=True)

    def __init__(self,
                 name,
                 id,
                 description,
                 public):
        self.name = name
        self.id = id
        self.description = description
        self.public = public
