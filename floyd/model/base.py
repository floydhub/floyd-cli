class BaseModel(object):

    def to_dict(self):
        return self.schema.dump(self).data

    @classmethod
    def from_dict(cls, dct):
        return cls.schema.load(dct).data
