import sys
import time
import json
import base64
from marshmallow import Schema, fields, post_load

from floyd.model.base import BaseModel


def assert_token_not_expired(token):
    payload_base64 = token.split('.')[1] + '==='
    payload = json.loads(base64.decodestring(payload_base64))
    if payload['exp'] <= time.time():
        sys.exit('ERROR: Auth token expired, please use "floyd login" command to login with a new token.')


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
        assert_token_not_expired(token)
        self.username = username
        self.token = token
