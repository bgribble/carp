import asyncio
import random
from collections import defaultdict

from uuid import uuid4

from carp.service import Service, CallData, CallResponse
from carp.channel import Channel
from carp.serializer import Serializer, Serializable

class RemoteExecutionError(Exception):
    pass

class HostAnnounce(Serializable):
    def __init__(self, *, host_id):
        self.host_id = host_id
        super().__init__()

    def to_dict(self):
        return dict(
            host_id=self.host_id
        )


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
        self.calls_active = {}
        self.hosts_remote = {}
        self.listen_channel = None
        self.tasks = []
        self.status = Host.STOPPED
        self.on_accept = on_accept
        self.on_connect = on_connect
        self.on_message = on_message

    def _report_services(self):
        host_map = HostExports(
            host_id=self.id,
            exports=list(self.services_local.keys())
        ).serialize()
        for channel in self.hosts_remote.values():
            channel.put(host_map)

    async def start(self, channel: Channel):
        """
        Start the host, accepting connections on the specified
        Channel
        """
        self.listen_channel = channel
        self.status = Host.STARTED
        listener = asyncio.create_task(channel.serve(on_connect=self.accept))
        self.tasks.append(listener)
        await listener

    async def stop(self):
        self.status = Host.STOPPED
        to_cancel = self.tasks
        self.tasks = []
        for t in to_cancel:
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                pass

    async def accept(self, channel):
        if self.on_accept:
            await self.on_accept(channel)

        channel.put(HostAnnounce(host_id=self.id).serialize())
        self.tasks.append(asyncio.create_task(self._message_loop(channel)))

    async def connect(self, channel):
        self.status = Host.STARTED
        await channel.connect()
        if self.on_connect:
            await self.on_connect(channel)

        channel.put(HostAnnounce(host_id=self.id).serialize())
        self.tasks.append(asyncio.create_task(self._message_loop(channel)))

    async def _message_loop(self, channel):
        async def _process(bdata):
            message = Serializer.deserialize(bdata)

            if self.on_message:
                await self.on_message(message)

            # process broadcasts by peers
            if isinstance(message, HostAnnounce):
                self.hosts_remote[message.host_id] = channel
                self._report_services()
            elif isinstance(message, HostExports):
                for service in message.exports:
                    if message.host_id not in self.services_remote[service]:
                        self.services_remote[service].append(message.host_id)
                self.services_event.set()
            elif isinstance(message, CallData):
                service = self.services_local.get(message.service_name)
                call_return = None
                exception = None

                try:
                    call_return = await service(*message.args, **message.kwargs)
                except Exception as e:
                    exception = type(e).__name__

                response = CallResponse(
                    call_id=message.call_id,
                    service_name=service.name,
                    host_id=message.host_id,
                    value=call_return,
                    exception=exception,
                )
                channel.put(response.serialize())
            elif isinstance(message, CallResponse):
                call_data = self.calls_active.get(message.call_id)
                call_data.response = message
                call_data.event.set()

        first_message = True
        while (
            self.status == Host.STARTED
            and channel.status == Channel.CONNECTED
        ):
            message_bytes = await channel.get()
            if first_message:
                await _process(message_bytes)
                first_message = False
            else:
                asyncio.create_task(_process(message_bytes))

    async def export(self, service: Service):
        """
        Announce that a service is available on this host
        """
        self.services_local[service.name] = service
        service.is_remote = False
        service.host = self
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

        service.host = self
        if service.name in self.services_local:
            service.is_remote = False
            service.host_id = self.id
        elif service.name in self.services_remote:
            service.host_id = random.choice(self.services_remote[service.name])
            service.is_remote = True

    async def call(self, service, *args, **kwargs):
        """
        Send a request to a remote service, waiting for a
        response
        """

        call_data = CallData(
            service_name=service.name,
            host_id=service.host_id,
            args=args,
            kwargs=kwargs
        )
        channel = self.hosts_remote[service.host_id]
        self.calls_active[call_data.call_id] = call_data
        channel.put(call_data.serialize())
        await call_data.event.wait()
        del self.calls_active[call_data.call_id]
        if call_data.response.exception:
            raise RemoteExecutionError(call_data.response.exception)

        return call_data.response.value

    async def handle(self, service, data):
        """
        Handle a remote request
        """
