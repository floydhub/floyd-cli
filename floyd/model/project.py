from marshmallow import Schema, fields, post_load

from floyd.model.base import BaseModel


class ProjectSchema(Schema):
    """
    Project schema
    """
    name = fields.Str()
    id = fields.Str()
    description = fields.Str(allow_none=True)
    public = fields.Boolean()
    public = fields.Boolean()
    latest_experiment_name = fields.Str(allow_none=True)

    @post_load
    def make_credentials(self, data):
        return Project(**data)


class Project(BaseModel):
    """
    Latest version is the newest cli available on PIP
    Minimum version is the version below which CLI should fail
    """
    schema = ProjectSchema(strict=True)

    def __init__(self,
                 name,
                 id,
                 description,
                 public,
                 latest_experiment_name):
        self.name = name
        self.id = id
        self.description = description
        self.public = public
        self.latest_experiment_name = latest_experiment_name
