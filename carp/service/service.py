"""
service.py -- Service base class
"""


class Service:
    def __init__(self, name):
        self.name = name
        self.host = None
        self.host_id = None
        self.instance_id = None
        self.is_remote = False

    @staticmethod
    def build(impl_object):
        factory = None
        if hasattr(impl_object, '_service_type'):
            factory = impl_object._service_type
        
        return factory(impl_object)
