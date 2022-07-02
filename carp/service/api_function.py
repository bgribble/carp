
from .service import Service

def apifunc(func):
    """
    Decorator for standalone API functions
    """
    return ApiFunction(func)
    


class ApiFunction(Service):
    def __init__(self, func: callable):
        self.func = func
        super().__init__(func.__name__)

    async def __call__(self, *args, **kwargs):
        if self.is_remote:
            rv = await self.host.call(self, dict(args=args, kwagrs=kwargs))
        else:
            rv = await self.func(*args, **kwargs)
        return rv
