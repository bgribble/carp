from abc import ABC, abstractmethod

class Serializer(ABC):
    @abstractmethod
    def serialize(self, pyobj: any) -> bytes:
        pass

    @abstractmethod
    def deserialize(self, bytestr: bytes) -> any:
        pass
