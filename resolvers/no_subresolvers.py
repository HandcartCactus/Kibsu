from lxml import etree
from typing import Dict
from .base import Resolver


class NoSubResolvers(metaclass=Resolver):
    def __init__(self, resolvers: Dict[str, Resolver]):
        self.resolvers = resolvers
        self.include = False
        self.resolver_type = 'NoSubResolvers'
    
    def does_resolve(self, element: etree._Element):
        return all(not resolver.does_resolve(element) for resolver in self.resolvers.values())
    
    def resolve(self, element: etree._Element):
        #raise ValueError('The type NoResolvers does not support resolving. If `resolver.include==False`, you cannot call resolver.resolve().')
        return None
    
    def debug(self, element: etree._Element):
        debug = super().debug(element)
        debug['subresolvers'] = {resolver_name: resolver.debug(element) for resolver_name, resolver in self.resolvers.items()}
        return debug