
import json
import datetime
from dateutil import parser
from .serializer import Serializer
from .serializable import Serializable


class CarpJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        from .serializable import Serializable
        if isinstance(obj, datetime.datetime):
            return dict(__datetime__=True, value=obj.isoformat())
        if isinstance(obj, datetime.date):
            return dict(__date__=True, value=obj.isoformat())
        if isinstance(obj, Serializable):
            return dict(__serializable__=True, value=obj.serialize())
        return json.JSONEncoder.default(self, obj)


def decode_hook(obj):
    if isinstance(obj, dict) and "__datetime__" in obj:
        return parser.isoparse(obj["value"])
    if isinstance(obj, dict) and "__date__" in obj:
        return parser.isoparse(obj["value"]).date()
    if isinstance(obj, dict) and "__serializable__" in obj:
        return Serializer.deserialize(obj["value"])
    return obj


class JsonSerializer(Serializer):
    label = "json"

    def __init__(self, **serialize_options):
        self.serialize_options = serialize_options

    def serialize(self, pyobj):
        if isinstance(pyobj, dict):
            obj_dict = pyobj
            obj_dict['__type__'] = type(pyobj).__name__
        elif hasattr(pyobj, 'to_dict'):
            obj_dict = pyobj.to_dict()
            obj_dict['__type__'] = type(pyobj).__name__
        else:
            obj_dict = dict(__value__=pyobj)

        payload = json.dumps(
            obj_dict,
            **self.serialize_options,
            cls=CarpJSONEncoder
        )
        return f"{self.label}:{payload}".encode('utf-8')

    def deserialize(self, bytestr):
        obj_dict = json.loads(bytestr.decode(), object_hook=decode_hook)
        if '__type__' in obj_dict:
            typename = obj_dict['__type__']
            del obj_dict['__type__']

            if typename == 'dict':
                del obj_dict['__type__']
                return obj_dict

            typeobj = Serializable.registry.get(typename)
            if not typeobj:
                raise ValueError(f"[deserialize] Type obj not found for {typename}")
            if hasattr(typeobj, 'from_dict'):
                return typeobj.from_dict(obj_dict)
            else:
                return typeobj(**obj_dict)

        elif '__value__' in obj_dict:
            return obj_dict['__value__']
        else:
            return obj_dict
