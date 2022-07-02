import unittest
import asyncio
import tempfile
from carp.channel import UnixSocketChannel
from carp.host import Host
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

        async def accept(channel):
            server_conn.set()

        async def connect(channel):
            client_conn.set()

        server_channel = UnixSocketChannel(socket_path=self.sockname)
        server_host = Host(on_accept=accept)

        client_channel = UnixSocketChannel(socket_path=self.sockname)
        client_host = Host(on_connect=connect)

        await server_host.start(server_channel)
        await client_host.connect(client_channel)
        await server_conn.wait()
        await client_conn.wait()

    async def test_message(self):
        """
        A pair of hosts, one in server mode, can make a connection
        and send a message
        """
        message_recvd = asyncio.Event()
        messages = []

        async def message(msg):
            message_recvd.set()
            messages.append(msg)

        server_channel = UnixSocketChannel(socket_path=self.sockname)
        server_host = Host(on_message=message)

        client_channel = UnixSocketChannel(socket_path=self.sockname)
        client_host = Host()

        await server_host.start(server_channel)
        await client_host.connect(client_channel)
        message = 'hello, world'
        client_channel.put(Serializer.serialize(message))
        await message_recvd.wait()
        self.assertEqual(messages, [message])

