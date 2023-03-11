import asyncio
from asyncio import IncompleteReadError

from .channel import Channel
from .exceptions import ConnectionStatusError, ChannelError


class UnixSocketChannel(Channel):
    SYNC_MAGIC = b"[ SYNC ]"
    MAX_MESSAGE_SIZE = 65535

    def __init__(self, *, socket_path: str):
        self.socket_path = socket_path
        self.status = Channel.CLOSED
        self.reader = None
        self.writer = None
        self.server = None

    async def connect(self):
        self.status = Channel.CONNECTING
        reader, writer = await asyncio.open_unix_connection(self.socket_path)
        self.reader = reader
        self.writer = writer
        self.status = Channel.CONNECTED

    async def close(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            self.writer = None
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
        self.status = Channel.CLOSED

    async def serve(self, *, on_connect):
        async def _connected_cb(reader, writer):
            connected = UnixSocketChannel(socket_path=self.socket_path)
            connected.reader = reader
            connected.writer = writer
            connected.status = Channel.CONNECTED
            if asyncio.iscoroutinefunction(on_connect):
                await on_connect(connected)
            else:
                on_connect(connected)
        self.status = Channel.SERVING
        self.server = await asyncio.start_unix_server(
            _connected_cb, path=self.socket_path
        )

    async def put(self, message: bytes):
        if self.status != Channel.CONNECTED:
            raise ConnectionStatusError
        try:
            self.writer.write(self.SYNC_MAGIC)
            self.writer.write(b"% 8d" % len(message))
            self.writer.write(message)
            await self.writer.drain()
        except Exception as e:
            self.status = Channel.CLOSED
            raise ConnectionError("Connection closed during write")

    async def get(self):
        magiclen = len(self.SYNC_MAGIC)
        msglength = None
        badlength = False
        try:
            syncblock = await self.reader.readexactly(magiclen + 8)
            while msglength is None:
                if badlength or syncblock[:magiclen] != self.SYNC_MAGIC:
                    syncblock = syncblock[1:] + await self.reader.readexactly(1)
                    badlength = False
                    continue
                try:
                    msglength = int(syncblock[magiclen:])
                except ValueError:
                    badlength = True
                    continue

                if msglength < 0 or msglength > self.MAX_MESSAGE_SIZE:
                    badlength = True
                    msglength = None

            return await self.reader.readexactly(msglength)

        except IncompleteReadError as e:
            self.status = Channel.CLOSED
            raise ChannelError("Connection closed during read")
