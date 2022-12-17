from .service import Service
from .api_function import ApiFunction
from .call_data import CallData, CallResponse
from .api_class import ApiClass, apiclass, ApiProxyObject, ApiMethod, ApiNonInstanceMethod

def noresp(method):
    method.needs_response = False
    return method


