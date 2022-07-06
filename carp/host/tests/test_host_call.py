import asyncio
import tempfile
from carp.channel import UnixSocketChannel
from carp.service import ApiFunction
from carp.host import Host

from unittest import IsolatedAsyncioTestCase


class TestHostCall(IsolatedAsyncioTestCase):

    def setUp(self):
        self.sockname = tempfile.mktemp()

    async def test_call_locally(self):
        """
        A service that is local to the caller can be used
        """
        server_channel = UnixSocketChannel(socket_path=self.sockname)
        server_host = Host()

        client_channel = UnixSocketChannel(socket_path=self.sockname)
        client_host = Host()

        await server_host.start(server_channel)
        await client_host.connect(client_channel)

        func_called = asyncio.Event()

        async def svc_func():
            func_called.set()
            return True

        clnt_svc = ApiFunction(svc_func)

        await client_host.export(clnt_svc)
        await client_host.use(clnt_svc)

        result = await clnt_svc()

        self.assertEqual(result, True)

        await client_host.stop()
        await server_host.stop()


    async def test_call_serv_to_client_remotely(self):
        """
        A service that is remote from the caller can be used
        """
        server_channel = UnixSocketChannel(socket_path=self.sockname)
        server_host = Host()

        client_channel = UnixSocketChannel(socket_path=self.sockname)
        client_host = Host()

        await server_host.start(server_channel)
        await client_host.connect(client_channel)

        func_called = asyncio.Event()

        async def svc_func():
            func_called.set()
            return True

        server_svc = ApiFunction(svc_func)
        client_svc = ApiFunction(svc_func)

        await client_host.export(client_svc)
        await server_host.use(server_svc)

        result = await server_svc()
        self.assertEqual(result, True)

        await client_host.stop()
        await server_host.stop()

    async def test_call_client_to_serv_remotely(self):
        """
        A service that is remote from the caller can be used
        """
        server_channel = UnixSocketChannel(socket_path=self.sockname)
        server_host = Host()

        client_channel = UnixSocketChannel(socket_path=self.sockname)
        client_host = Host()

        await server_host.start(server_channel)
        await client_host.connect(client_channel)

        func_called = asyncio.Event()

        async def svc_func():
            func_called.set()
            return True

        server_svc = ApiFunction(svc_func)
        client_svc = ApiFunction(svc_func)

        await server_host.export(client_svc)
        await client_host.use(server_svc)

        result = await client_svc()
        self.assertEqual(result, True)

        await client_host.stop()
        await server_host.stop()

