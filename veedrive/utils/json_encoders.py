import json
from uuid import UUID


def uuid_encoder(obj):
    if isinstance(obj, UUID):
        return str(obj)
    return obj


class VeeDriveJSONEncoder(json.JSONEncoder):
    encoders = [
        uuid_encoder,
    ]

    def default(self, obj):
        result = obj
        for encoder in self.encoders:
            result = encoder(obj)
        return result
