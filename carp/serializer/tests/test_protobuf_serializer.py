import datetime
import random

from unittest import TestCase

from carp.serializer import Serializable, Serializer, ProtobufSerializer
from carp.serializer.protobuf.pytypes_pb2 import (
    PythonValueContainer,
    PythonArrayContainer,
    PythonDictContainer
)

class PValue(Serializable):
    serializer = ProtobufSerializer
    protobuf_type = PythonValueContainer

    def __init__(self, value):
        self.value = value

class PArray(Serializable):
    serializer = ProtobufSerializer
    protobuf_type = PythonArrayContainer

    def __init__(self, value):
        self.value = value

class PDict(Serializable):
    serializer = ProtobufSerializer
    protobuf_type = PythonDictContainer

    def __init__(self, value):
        self.value = value

class TestProtobufSerializer(TestCase):
    def test_pyvalue_types(self):
        """
        PythonValue protobuf message works as expected
        """
        values = [
            (123.4,),
            (12,),
            ("hello, world!",),
            (dict(a=1, b=2, c="hello", d=False),),
            ((1,2,3), [1,2,3]),
            (True,),
            (False,),
            (None,),
        ]

        for v in values:
            val = PValue(v[0])
            expected = v[1] if len(v) > 1 else v[0]

            serialized = val.serialize()

            deserialized = Serializer.deserialize(serialized)
            self.assertEqual(expected, deserialized.value)
            self.assertEqual(type(expected), type(deserialized.value))

    def test_python_array(self):
        """
        PythonArray protobuf message works as expected
        """
        val = [
            random.randint(1,1000000) for _ in range(100)
        ]
        pv = PArray(val)

        serialized = pv.serialize()

        deserialized = Serializer.deserialize(serialized)
        self.assertEqual(val, deserialized.value)


    def test_python_dict(self):
        """
        PythonArray protobuf message works as expected
        """
        val = {
            "a": 1,
            "b": 2,
            "c": True,
            "d": None
        }

        pv = PDict(val)

        serialized = pv.serialize()
        deserialized = Serializer.deserialize(serialized)
        self.assertIsInstance(deserialized, PDict)
        self.assertIsInstance(deserialized.value, dict)
        self.assertEqual(val, deserialized.value)
