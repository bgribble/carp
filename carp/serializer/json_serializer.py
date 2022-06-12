
import json
import datetime
from dateutil import parser

from carp.serializer import Serializer

class CarpJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return dict(__datetime__=True, value=obj.isoformat())
        if isinstance(obj, datetime.date):
            return dict(__date__=True, value=obj.isoformat())
        return json.JSONEncoder.default(self, obj)

def decode_hook(obj):
    if isinstance(obj, dict) and "__datetime__" in obj:
        return parser.isoparse(obj["value"]) 
    elif isinstance(obj, dict) and "__date__" in obj:
        return parser.isoparse(obj["value"]).date() 
    return obj

class JsonSerializer(Serializer):

    def __init__(self, **serialize_options):
        self.serialize_options = serialize_options

    def serialize(self, pyobj):
        return json.dumps(pyobj, **self.serialize_options, cls=CarpJSONEncoder).encode('utf-8')

    def deserialize(self, bytestr):
        return json.loads(bytestr.decode(), object_hook=decode_hook)
