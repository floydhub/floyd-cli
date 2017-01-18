from marshmallow import Schema, fields, post_load


class CredentialsSchema(Schema):
    """
    Floyd credentials schema
    """
    username = fields.Str()
    password = fields.Str()

    @post_load
    def make_credentials(self, data):
        return Credentials(**data)


class Credentials(object):
    """
    Floyd credentials consists of username and password
    """
    schema = CredentialsSchema()

    def __init__(self,
                 username,
                 password):
        self.username = username
        self.password = password

    def to_dict(self):
        return self.schema.dump(self).data

    @classmethod
    def from_dict(cls, dct):
        return cls.schema.load(dct).data
