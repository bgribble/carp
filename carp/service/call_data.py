import asyncio
from carp.serializer import Serializable


class CallData(Serializable):
    call_counter = 0

    def __init__(self, *, call_id=None, service_name, host_id, args, kwargs):
        if call_id is None:
            self.call_id = CallData.call_counter
            CallData.call_counter += 1
        else:
            self.call_id=call_id

        self.service_name = service_name
        self.host_id = host_id
        self.args = args
        self.kwargs = kwargs
        self.event = asyncio.Event()
        self.response = None

    def to_dict(self):
        return dict(
            call_id=self.call_id,
            host_id=self.host_id,
            service_name=self.service_name,
            args=self.args,
            kwargs=self.kwargs,
        )


class CallResponse(Serializable):
    def __init__(self, *, call_id, service_name, host_id, value):
        self.call_id = call_id
        self.service_name = service_name
        self.host_id = host_id
        self.value = value

    def to_dict(self):
        return dict(
            call_id=self.call_id,
            service_name=self.service_name,
            host_id=self.host_id,
            value=self.value
        )
