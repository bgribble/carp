import datetime
from unittest import TestCase

from carp.serializer import JsonSerializer

pretty = b"""json:{
    "a": 1,
    "b": 2,
    "c": "hello",
    "__type__": "dict"
}"""

class TestJsonSerializer(TestCase):

    def test_serialize__no_options(self):
        """
        JSON serializer works for basic object
        """
        js = JsonSerializer()
        serialized = js.serialize(dict(a=1, b=2, c="hello"))
        self.assertEqual(
            serialized,
            b'json:{"a": 1, "b": 2, "c": "hello", "__type__": "dict"}'
        )

    def test_serialize__pretty(self):
        """
        JSON serializer works for basic object with options passed in
        """
        js = JsonSerializer(indent=4)
        serialized = js.serialize(dict(a=1, b=2, c="hello"))
        self.assertEqual(serialized, pretty)


    def test_serialize__times(self):
        """
        JSON serializer works for datetime objects
        """
        now = datetime.datetime.utcnow()

        js = JsonSerializer()
        self.assertEqual(
            js.serialize(dict(ts=now)),
            f'json:{{"ts": {{"__datetime__": true, "value": "{now.isoformat()}"}}, "__type__": "dict"}}'.encode('utf-8')
        )
        self.assertEqual(
            js.serialize(dict(ts=now.date())),
            f'json:{{"ts": {{"__date__": true, "value": "{now.date().isoformat()}"}}, "__type__": "dict"}}'.encode('utf-8')
        )

    def test_serialize__tuple(self):
        """
        JSON serializer works for tuple
        """
        js = JsonSerializer()
        serialized = js.serialize(dict(a=(1, 2, 3)))
        self.assertEqual(
            serialized,
            b'json:{"a": [1, 2, 3], "__type__": "dict"}'
        )

    def test_deserialize__basic(self):
        """
        JSON deserializer works for basic object
        """
        js = JsonSerializer()
        obj = js.deserialize(
            b'{"a": 1, "b": 2, "c": "hello"}'
        )
        self.assertEqual(
            obj,
            dict(a=1, b=2, c="hello")
        )
