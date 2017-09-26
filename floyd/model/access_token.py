from marshmallow import Schema, fields, post_load

from floyd.model.base import BaseModel


class AccessTokenSchema(Schema):

    username = fields.Str()
    token = fields.Str()

    @post_load
    def make_access_token(self, data):
        return AccessToken(**data)


class AccessToken(BaseModel):

    schema = AccessTokenSchema(strict=True)

    def __init__(self,
                 username,
                 token):
        self.username = username
        self.token = token
