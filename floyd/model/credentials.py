from marshmallow import Schema, fields, post_load

from floyd.model.base import BaseModel


class CredentialsSchema(Schema):
    """
    Floyd credentials schema
    """
    username = fields.Str()
    password = fields.Str()

    @post_load
    def make_credentials(self, data):
        return Credentials(**data)


class Credentials(BaseModel):
    """
    Floyd credentials consists of username and password
    """
    schema = CredentialsSchema(strict=True)

    def __init__(self,
                 username,
                 password):
        self.username = username
        self.password = password

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
        }
