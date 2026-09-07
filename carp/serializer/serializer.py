
class Serializer:
    serializers = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Serializer.serializers[cls.label] = cls

    @staticmethod
    def serialize(obj):
        from .serializable import Serializable
        from .json_serializer import JsonSerializer
        if isinstance(obj, Serializable):
            return obj.serialize()

        return JsonSerializer().serialize(obj)

    @staticmethod
    def deserialize(bytestr: bytes) -> any:
        try:
            serializer_label, data = bytestr.split(b":", 1)
        except Exception as e:
            raise ValueError(f"No serializer label in data packet {bytestr}")

        serializer = Serializer.serializers.get(serializer_label.decode())
        if serializer:
            try:
                return serializer().deserialize(data)
            except Exception as e:
                raise ValueError(f"Exception in deserializer: {e} {bytestr}")
        raise ValueError(f"Serializer '{serializer_label}' not found: {bytestr}")
