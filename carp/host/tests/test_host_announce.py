import asyncio
import tempfile
from carp.channel import UnixSocketChannel
from carp.service import ApiFunction
from carp.host import Host

from unittest import IsolatedAsyncioTestCase


class TestHostAnnounce(IsolatedAsyncioTestCase):

    def setUp(self):
        self.sockname = tempfile.mktemp()

    async def test_client_export_service(self):
        """
        A pair of hosts, one in server mode, can make a connection
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

        await client_host.export(svc_func)
        clnt_svc = await server_host.require(svc_func)

        self.assertIn(clnt_svc.name, client_host.services_local)
        self.assertIn(clnt_svc.name, server_host.services_remote)
        self.assertEqual(
            server_host.services_remote[clnt_svc.name][0],
            client_host.id
        )
        await client_host.stop()
        await server_host.stop()

    async def test_server_export_service(self):
        """
        A pair of hosts, one in server mode, can make a connection
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

        await server_host.export(svc_func)
        clnt_svc = await client_host.require(svc_func)

        self.assertIn(clnt_svc.name, server_host.services_local)
        self.assertIn(clnt_svc.name, client_host.services_remote)
        self.assertEqual(
            client_host.services_remote[clnt_svc.name][0],
            server_host.id
        )
        await client_host.stop()
        await server_host.stop()



