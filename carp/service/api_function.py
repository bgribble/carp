
from .service import Service

def apifunc(func: callable) -> callable:
    """
    Decorator for standalone API functions
    """
    func._service_type = ApiFunction
    func._service_name = func.__name__
    return func


class ApiFunction(Service):
    def __init__(self, func: callable):
        self.func = func
        self.host = None
        name = func.__name__
        if hasattr(func, '_service_name'):
            name = func._service_name
        super().__init__(name)

    async def __call__(self, *args, **kwargs):
        needs_response = getattr(self.func, "needs_response", True)

        if self.is_remote:
            rv = await self.host.call(self, args, kwargs, response=needs_response)
        else:
            rv = await self.func(*args, **kwargs)
        return rv
