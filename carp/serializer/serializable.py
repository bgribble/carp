"""
Mixin class to provide hooks for Carp to serialize and deserialize
objects

Default implementation uses JSON
"""


class Serializable:
    registry = {}
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Serializable.registry[cls.__name__] = cls

    def serialize(self):
        from .json_serializer import JsonSerializer
        # defaults to JsonSerializer
        return JsonSerializer().serialize(self)
    

