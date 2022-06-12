
from abc import ABC, abstractmethod

class Channel(ABC):
    CLOSED = "closed"
    CONNECTED = "connected"
    CONNECTING = "connecting"
    SERVING = "serving"

    @abstractmethod
    async def serve(self):
        pass

    @abstractmethod
    async def connect(self, **config):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def put(self, message):
        pass

    @abstractmethod
    async def get(self):
        pass



