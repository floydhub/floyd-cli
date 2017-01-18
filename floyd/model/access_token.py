from marshmallow import Schema, fields, post_load


class AccessTokenSchema(Schema):

    token = fields.Str()
    expiry = fields.Number()

    @post_load
    def make_access_token(self, data):
        return AccessToken(**data)


class AccessToken(object):

    schema = AccessTokenSchema()

    def __init__(self,
                 token,
                 expiry=None):
        self.token = token
        self.expiry = expiry

    def to_dict(self):
        return self.schema.dump(self).data

    @classmethod
    def from_dict(cls, dct):
        return cls.schema.load(dct).data
