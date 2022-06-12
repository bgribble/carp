import datetime
from unittest import TestCase

from carp.serializer import JsonSerializer

pretty = b"""{
    "a": 1,
    "b": 2,
    "c": "hello"
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
            b'{"a": 1, "b": 2, "c": "hello"}'
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
            f'{{"ts": {{"__datetime__": true, "value": "{now.isoformat()}"}}}}'.encode('utf-8')
        )
        self.assertEqual(
            js.serialize(dict(ts=now.date())),
            f'{{"ts": {{"__date__": true, "value": "{now.date().isoformat()}"}}}}'.encode('utf-8')
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
