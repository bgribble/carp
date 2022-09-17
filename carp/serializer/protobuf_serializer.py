from carp.serializer import Serializable, Serializer
from carp.serializer.protobuf.envelope_pb2 import Envelope
from carp.serializer.protobuf.pytypes_pb2 import (
    PythonDict,
    PythonArray,
    PythonValue
)

SCALAR_TYPES = (int, float, str, bool)


class ProtobufSerializer(Serializer):
    label = "pb2"

    def __init__(self, **serialize_options):
        self.serialize_options = serialize_options
        super().__init__()

    def _pb2_value(self, val, pb=None):
        if not pb:
            pb = PythonValue()
        if isinstance(val, Serializable):
            pb._serialized = val.serialize()
        elif isinstance(val, str):
            pb._string = val
        elif isinstance(val, bytes):
            pb._bytes = val
        elif isinstance(val, int):
            pb._int = val
        elif isinstance(val, float):
            pb._double = val
        elif isinstance(val, bool):
            pb._bool = val
        elif isinstance(val, type(None)):
            pb._none = True
        elif isinstance(val, dict):
            pbdict = PythonDict()
            for key, value in val.items():
                pbitem = pbdict.items.add()
                pbitem.key.CopyFrom(self._pb2_value(key))
                pbitem.value.CopyFrom(self._pb2_value(value))
            pb._dict.CopyFrom(pbdict)
        elif isinstance(val, (list, tuple)):
            pbarray = PythonArray()
            for v in val:
                pbval = pbarray.items.add()
                pbval = self._pb2_value(v, pb=pbval)
            pb._array.CopyFrom(pbarray)
        return pb

    def _python_value(self, pb_val):
        if isinstance(pb_val, PythonArray):
            return [
                self._python_value(v) for v in pb_val.items
            ]
        elif isinstance(pb_val, PythonDict):
            return {
                self._python_value(i.key): self._python_value(i.value)
                for i in pb_val.items
            }
        elif isinstance(pb_val, PythonValue):
            py_type = pb_val.WhichOneof("value_types")
            if py_type == "_serialized":
                return Serializer.deserialize(pb_val._serialized)
            elif py_type == "_array":
                return self._python_value(pb_val._array)
            elif py_type == "_dict":
                return self._python_value(pb_val._dict)
            elif py_type == "_none":
                return None
            elif py_type:
                return getattr(pb_val, py_type)
            return None
        else:
            return pb_val

    def serialize(self, pyobj):
        obj_pb = pyobj.protobuf_type()
        obj_dict = {
            field.name: getattr(pyobj, field.name)
            for field in obj_pb.DESCRIPTOR.fields
        }

        obj_typename = type(pyobj).__name__

        for key, value in obj_dict.items():
            if isinstance(value, Serializable):
                val_pb = PythonValue()
                val_pb._serialized = value.serialize()
                setattr(obj_pb, key, val_pb)
            elif isinstance(value, SCALAR_TYPES):
                setattr(obj_pb, key, value)
            elif isinstance(value, dict):
                dict_pb = getattr(obj_pb, key)
                for dkey, dval in value.items():
                    ditem = dict_pb.items.add(
                        key=self._pb2_value(key),
                        value=self._pb2_value(dval)
                    )
            elif isinstance(value, (list, tuple)):
                array_pb = getattr(obj_pb, key)
                for dval in value:
                    ditem = array_pb.items.add()
                    ditem.CopyFrom(self._pb2_value(dval))

        envelope = Envelope()
        envelope.content_type = obj_typename
        envelope.content = obj_pb.SerializeToString()
        return f"{self.label}".encode('utf-8') + b':' + envelope.SerializeToString()

    def deserialize(self, bytestr):
        envelope = Envelope()
        envelope.ParseFromString(bytestr)

        # find the type object of the contents
        type_obj = Serializable.registry.get(envelope.content_type)
        if not type_obj:
            raise ValueError(f"No Serializable type for '{envelope.content_type}'")

        # deserialize the contents
        proto_obj = type_obj.protobuf_type()
        proto_obj.ParseFromString(envelope.content)

        obj_dict = {}
        for field in proto_obj.DESCRIPTOR.fields:
            raw_value = getattr(proto_obj, field.name)
            obj_dict[field.name] = self._python_value(raw_value)

        return type_obj(**obj_dict)
