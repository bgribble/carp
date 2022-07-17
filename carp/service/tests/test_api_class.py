import tempfile
from carp.channel import UnixSocketChannel
from carp.service import apiclass, ApiClass, ApiObject
from carp.host import Host, RemoteExecutionError

from unittest import IsolatedAsyncioTestCase


@apiclass
class RemoteObj:
    def __init__(self):
        self.counter = 0

    def set_counter(self, val):
        self.counter = val

    def get_counter(self):
        return self.counter


class TestApiClass(IsolatedAsyncioTestCase):

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

    async def test_create_obj(self):
        await self.server_host.export(RemoteObj)

        RemoteObjFactory = await self.client_host.require(RemoteObj)
        oo = await RemoteObjFactory()

        self.assertEqual(type(RemoteObjFactory), ApiClass)
        self.assertEqual(type(oo), ApiObject)

    async def test_change_state(self):
        await self.server_host.export(RemoteObj)

        RemoteObjFactory = await self.client_host.require(RemoteObj)
        oo = await RemoteObjFactory()

        self.assertEqual(await oo.get_counter(), 0)
        await oo.set_counter(99)
        self.assertEqual(await oo.get_counter(), 99)
