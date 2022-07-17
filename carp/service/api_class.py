import inspect
from collections import defaultdict

from .service import Service


def apiclass(cls):
    cls._service_type = ApiClass
    cls._service_name = cls.__name__
    return cls


class ApiObject:
    def __init__(self, service, instance_id):
        self.service = service
        self.host = service.host
        self.id = instance_id

    def __getattribute__(self, name):
        service = object.__getattribute__(self, 'service')
        id = object.__getattribute__(self, 'id')
        served_cls = service.served_cls

        served_meth = getattr(served_cls, name)
        if served_meth:
            return ApiMethod(service, name, id)


class ApiMethod(Service):
    def __init__(self, class_service, method_name, instance_id):
        self.instance_id = instance_id
        self.class_service = class_service
        self.method_name = method_name

        super().__init__(f"{class_service.name}.{method_name}")

    async def __call__(self, *args, **kwargs):
        if self.is_remote:
            rv = await self.host.call(self, *args, **kwargs)
        else:
            cls = self.class_service.served_cls
            instance = ApiClass.instance_map[self.class_service.name].get(self.instance_id)
            method = getattr(cls, self.method_name)
            rv = method(instance, *args, **kwargs)
            if inspect.isawaitable(rv):
                rv = await rv
        return rv


class ApiClass(Service):
    instance_map = defaultdict(dict)
    instance_next_id = 1

    def __init__(self, served_cls):
        self.served_cls = served_cls
        name = self.served_cls.__name__
        if hasattr(served_cls, '_service_name'):
            name = served_cls._service_name

        super().__init__(name)

    async def __call__(self, *args, **kwargs):
        """
        .__call__() implements the constructor, i.e. instance = ClassService()

        """
        if self.is_remote:
            instance_id = await self.host.call(self, *args, **kwargs)
            rv = ApiObject(self, instance_id)
        else:
            instance = self.served_cls(*args, **kwargs)
            if inspect.isawaitable(instance):
                instance = await instance
            instance_id = ApiClass.instance_next_id
            ApiClass.instance_next_id += 1
            ApiClass.instance_map[self.name][instance_id] = instance
            rv = instance_id

        return rv
