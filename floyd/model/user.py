from marshmallow import Schema, fields, post_load

from floyd.model.base import BaseModel


class UserSchema(Schema):
    uid = fields.Str()
    username = fields.Str()
    email = fields.Str()
    type = fields.Str(allow_none=True)

    @post_load
    def make_user(self, data):
        return User(**data)


class User(BaseModel):
    schema = UserSchema(strict=True)

    def __init__(self,
                 uid,
                 username,
                 email,
                 type):
        self.uid = uid
        self.username = username
        self.email = email
        self.type = type
