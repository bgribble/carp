import asyncio
import random
from collections import defaultdict

from uuid import uuid4

from carp.service import Service
from carp.channel import Channel
from carp.serializer import Serializer, Serializable


class HostExports(Serializable):
    def __init__(self, *, host_id, exports):
        self.host_id = host_id
        self.exports = exports
        super().__init__()

    def to_dict(self):
        return dict(
            host_id=self.host_id,
            exports=self.exports
        )


class Host:
    STOPPED = "stopped"
    STARTED = "started"

    def __init__(self, *, on_accept=None, on_connect=None, on_message=None):
        self.id = str(uuid4())

        self.services_remote = defaultdict(list)
        self.services_local = {}
        self.services_event = asyncio.Event()

        self.peer_channels = []
        self.listen_channel = None
        self.listen_task = None
        self.status = Host.STOPPED
        self.on_accept = on_accept
        self.on_connect = on_connect
        self.on_message = on_message

    def _report_services(self):
        host_map = HostExports(host_id=self.id, exports=list(self.services_local.keys())).serialize()
        for channel in self.peer_channels:
            channel.put(host_map)

    async def start(self, channel: Channel):
        """
        Start the host, accepting connections on the specified
        Channel
        """
        self.listen_channel = channel
        self.status = Host.STARTED
        self.listen_task = channel.serve(on_connect=self.accept)
        return await self.listen_task

    async def accept(self, channel):
        self.peer_channels.append(channel)
        if self.on_accept:
            await self.on_accept(channel)

        self._report_services()

        await self._message_loop(channel)

    async def connect(self, channel):
        await channel.connect()
        self.peer_channels.append(channel)
        if self.on_connect:
            await self.on_connect(channel)

        await self._message_loop(channel)

    async def _message_loop(self, channel):
        while (
            self.status == Host.STARTED
            and channel.status == Channel.CONNECTED
        ):
            message_bytes = await channel.get()
            message = Serializer.deserialize(message_bytes)

            if self.on_message:
                await self.on_message(message)

            # process broadcasts by peers
            if isinstance(message, HostExports):
                for service in message.exports:
                    if message.host_id not in self.services_remote[service]:
                        self.services_remote[service].append(message.host_id)
                self.services_event.set()

    async def announce(self, service: Service):
        """
        Announce that a service is available on this host
        """
        self.services_local[service.name] = service
        service.is_remote = False
        service.host_id = self.id
        self._report_services()
        self.services_event.set()

    async def use(self, service: Service):
        """
        Use a service announced by this or another host, waiting
        until it is available
        """
        while (
            service.name not in self.services_local
            and service.name not in self.services_remote
            and self.status == Host.STARTED
        ):
            await self.services_event.wait()
        if service.name in self.services_local:
            service.is_remote = False
            service.host_id = self.id
        elif service.name in self.services_remote:
            service.host_id = random.choice(self.services_remote[service.name])
            service.is_remote = True

    async def call(self, service, data):
        """
        Send a request to a remote service, waiting for a
        response
        """

    async def handle(self, service, data):
        """
        Handle a remote request
        """
