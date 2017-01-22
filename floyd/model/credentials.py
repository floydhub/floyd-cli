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


class SignupRequestSchema(Schema):
    """
    Floyd signup schema
    """
    username = fields.Str()
    password = fields.Str()
    password_confirmation = fields.Str()
    email = fields.Str()
    invite_code = fields.Str()

    @post_load
    def make_credentials(self, data):
        return SignupRequest(**data)


class SignupRequest(BaseModel):
    """
    Floyd credentials consists of username and password
    """
    schema = SignupRequestSchema(strict=True)

    def __init__(self,
                 username,
                 password,
                 password_confirmation,
                 email,
                 invite_code=None):
        self.username = username
        self.password = password
        self.password_confirmation = password_confirmation
        self.email = email
        self.invite_code = invite_code
