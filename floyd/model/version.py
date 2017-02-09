from marshmallow import Schema, fields, post_load

from floyd.model.base import BaseModel


class CliVersionSchema(Schema):
    """
    Floyd cli versions schema
    """
    latest_version = fields.Str()
    min_version = fields.Str()

    @post_load
    def make_credentials(self, data):
        return CliVersion(**data)


class CliVersion(BaseModel):
    """
    Latest version is the newest cli available on PIP
    Minimum version is the version below which CLI should fail
    """
    schema = CliVersionSchema(strict=True)

    def __init__(self,
                 latest_version,
                 min_version):
        self.latest_version = latest_version
        self.min_version = min_version
