import asyncio
from carp.serializer import Serializable, ProtobufSerializer
from carp.serializer.protobuf import call_data_pb2


class CallData(Serializable):
    """
    CallData is the generic wrapper for a remote method or function
    call. It packages up the args and the identity of the called
    object and provides an asyncio.Event() which will be notified when
    the remote call is complete.
    """
    serializer = ProtobufSerializer
    protobuf_type = call_data_pb2.CallData
    call_counter = 0

    def __init__(self, *, call_id=None, instance_id=None, service_name, host_id, args, kwargs):
        if call_id is None:
            self.call_id = CallData.call_counter
            CallData.call_counter += 1
        else:
            self.call_id = call_id

        self.service_name = service_name
        self.host_id = host_id
        self.instance_id = instance_id
        self.args = args or []
        self.kwargs = kwargs or {}
        self.event = asyncio.Event()
        self.response = None


class CallResponse(Serializable):
    """
    CallResponse is what you get back when the call is complete
    """
    serializer = ProtobufSerializer
    protobuf_type = call_data_pb2.CallResponse

    def __init__(self, *, call_id, service_name, host_id, value, exception):
        self.call_id = call_id
        self.service_name = service_name
        self.host_id = host_id
        self.value = value
        self.exception = exception

    def to_dict(self):
        return dict(
            call_id=self.call_id,
            service_name=self.service_name,
            host_id=self.host_id,
            value=self.value,
            exception=self.exception,
        )
