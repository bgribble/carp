import unittest
import asyncio
import tempfile
from carp.channel import UnixSocketChannel
from carp.host.host import Host, HostAnnounce
from carp.serializer import Serializer

from unittest import IsolatedAsyncioTestCase


class TestHostConnect(IsolatedAsyncioTestCase):

    def setUp(self):
        self.sockname = tempfile.mktemp()

    async def test_connect_back(self):
        """
        A pair of hosts, one in server mode, can make a connection
        """
        server_conn = asyncio.Event()
        client_conn = asyncio.Event()

        async def accept(event, channel):
            server_conn.set()

        async def connect(event, channel):
            client_conn.set()

        server_channel = UnixSocketChannel(socket_path=self.sockname)
        server_host = Host()
        server_host.on("accept", accept)

        client_channel = UnixSocketChannel(socket_path=self.sockname)
        client_host = Host()
        client_host.on("connect", connect)

        await server_host.start(server_channel)
        await client_host.connect(client_channel)
        await server_conn.wait()
        await client_conn.wait()

        await client_host.stop()
        await server_host.stop()

    async def test_message(self):
        """
        A pair of hosts, one in server mode, can make a connection
        and send a message
        """
        message_recvd = asyncio.Event()
        messages = []
        async def message(event, msg):
            messages.append(msg)
            message_recvd.set()

        server_channel = UnixSocketChannel(socket_path=self.sockname)
        server_host = Host()
        server_host.on("message", message)

        client_channel = UnixSocketChannel(socket_path=self.sockname)
        client_host = Host()

        await server_host.start(server_channel)
        await client_host.connect(client_channel)

        message = 'hello, world'
        await client_channel.put(Serializer.serialize(message))
        await message_recvd.wait()
        await client_host.stop()
        await server_host.stop()

        self.assertTrue(isinstance(messages[0], HostAnnounce))
        self.assertEqual(messages[1:], [message])
