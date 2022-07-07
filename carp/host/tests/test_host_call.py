import asyncio
import tempfile
from carp.channel import UnixSocketChannel
from carp.service import ApiFunction
from carp.host import Host, RemoteExecutionError

from unittest import IsolatedAsyncioTestCase


class TestHostCall(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.sockname = tempfile.mktemp()
        self.server_channel = UnixSocketChannel(socket_path=self.sockname)
        self.server_host = Host()
        self.client_channel = UnixSocketChannel(socket_path=self.sockname)
        self.client_host = Host()

        await self.server_host.start(self.server_channel)
        await self.client_host.connect(self.client_channel)


    async def asyncTearDown(self):
        await self.client_host.stop()
        await self.server_host.stop()

    async def test_call_locally(self):
        """
        A service that is local to the caller can be used
        """
        func_called = asyncio.Event()
        async def svc_func():
            func_called.set()
            return True

        clnt_svc = ApiFunction(svc_func)

        await self.client_host.export(clnt_svc)
        await self.client_host.use(clnt_svc)

        result = await clnt_svc()

        self.assertEqual(result, True)

    async def test_call_serv_to_client_remotely(self):
        """
        A service that is remote from the caller can be used
        """
        func_called = asyncio.Event()

        async def svc_func():
            func_called.set()
            return True

        server_svc = ApiFunction(svc_func)
        client_svc = ApiFunction(svc_func)

        await self.client_host.export(client_svc)
        await self.server_host.use(server_svc)

        result = await server_svc()
        self.assertEqual(result, True)

    async def test_call_client_to_serv_remotely(self):
        """
        A service that is remote from the caller can be used
        """
        func_called = asyncio.Event()

        async def svc_func():
            func_called.set()
            return True

        server_svc = ApiFunction(svc_func)
        client_svc = ApiFunction(svc_func)

        await self.server_host.export(server_svc)
        await self.client_host.use(client_svc)

        result = await client_svc()
        self.assertEqual(result, True)

    async def test_call_remotely__args(self):
        """
        A service with arguments works as expected
        """
        func_called = asyncio.Event()

        async def svc_func(arg1, arg2):
            func_called.set()
            return [arg1, arg2]

        server_svc = ApiFunction(svc_func)
        client_svc = ApiFunction(svc_func)

        await self.server_host.export(server_svc)
        await self.client_host.use(client_svc)

        test_values = [
            [12, 34],
            ["hello", "world"],
            [[12, 34, 56], [78, 90]],
            [dict(a=1, b=2), dict(c=3, d=4)]
        ]
        
        for v in test_values:
            result = await client_svc(*v)
            self.assertEqual(result, v)

    async def test_call_remotely__exception(self):
        """
        Remote service raising an exception raises one locally
        """
        func_called = asyncio.Event()

        async def svc_func():
            func_called.set()
            raise ValueError

        server_svc = ApiFunction(svc_func)
        client_svc = ApiFunction(svc_func)

        await self.server_host.export(server_svc)
        await self.client_host.use(client_svc)

        with self.assertRaises(RemoteExecutionError):
            await client_svc()
