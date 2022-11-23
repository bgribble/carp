import unittest
import asyncio
import tempfile
from carp.channel import Channel, UnixSocketChannel

from unittest import IsolatedAsyncioTestCase

class TestUnixSocketChannel(IsolatedAsyncioTestCase):

    def setUp(self):
        self.sockname = tempfile.mktemp()

    async def test_serve(self):
        """
        A client+server pair can make a connection
        """
        server = UnixSocketChannel(socket_path=self.sockname)
        client = UnixSocketChannel(socket_path=self.sockname)

        await server.serve(on_connect=lambda channel: None)

        self.assertEqual(server.status, Channel.SERVING)
        self.assertEqual(client.status, Channel.CLOSED)

        await client.connect()
        self.assertEqual(client.status, Channel.CONNECTED)

        await client.close()
        self.assertEqual(client.status, Channel.CLOSED)

        await server.close()
        self.assertEqual(server.status, Channel.CLOSED)

    async def test_client_message(self):
        """
        client can connect and send a message, which is received
        """
        message_recvd = asyncio.Event()
        messages = []

        async def on_connect(peer_channel):
            messages.append(await peer_channel.get())
            message_recvd.set()

        server = UnixSocketChannel(socket_path=self.sockname)
        client = UnixSocketChannel(socket_path=self.sockname)

        await server.serve(on_connect=on_connect)
        await client.connect()
        await client.put(b"test message")
        
        await message_recvd.wait()
        self.assertEqual(messages[0], b"test message")

    async def test_server_message(self):
        """
        client can connect and send a message, which is received
        """
        async def on_connect(peer_channel):
            await peer_channel.put(b"test message")

        server = UnixSocketChannel(socket_path=self.sockname)
        client = UnixSocketChannel(socket_path=self.sockname)

        await server.serve(on_connect=on_connect)
        await client.connect()
        message = await client.get() 
        self.assertEqual(message, b"test message")

    async def test_resync(self):
        """
        client can receive a message despite sync error 
        """
        async def on_connect(peer_channel):
            await peer_channel.put(b"test message 1")
            peer_channel.writer.write(b"XXX")
            await peer_channel.put(b"test message 2")

        server = UnixSocketChannel(socket_path=self.sockname)
        client = UnixSocketChannel(socket_path=self.sockname)

        await server.serve(on_connect=on_connect)
        await client.connect()
        
        msg_1 = await client.get()
        msg_2 = await client.get()
        self.assertEqual(msg_1, b"test message 1")
        self.assertEqual(msg_2, b"test message 2")

    async def test_bad_message_length__not_number(self):
        """
        client can receive a message despite sync error 
        """
        async def on_connect(peer_channel):
            peer_channel.writer.write(peer_channel.SYNC_MAGIC)
            peer_channel.writer.write(b"XXX")
            await peer_channel.put(b"test message")

        server = UnixSocketChannel(socket_path=self.sockname)
        client = UnixSocketChannel(socket_path=self.sockname)

        await server.serve(on_connect=on_connect)
        await client.connect()
        
        msg_1 = await client.get()
        self.assertEqual(msg_1, b"test message")

    async def test_bad_message_length__too_long(self):
        """
        client can receive a message despite sync error 
        """
        async def on_connect(peer_channel):
            peer_channel.writer.write(peer_channel.SYNC_MAGIC)
            peer_channel.writer.write(b'99999999') 
            peer_channel.writer.write(b'abc' * 100)
            await peer_channel.put(b"test message")

        server = UnixSocketChannel(socket_path=self.sockname)
        client = UnixSocketChannel(socket_path=self.sockname)

        await server.serve(on_connect=on_connect)
        await client.connect()
        
        msg_1 = await client.get()
        self.assertEqual(msg_1, b"test message")
