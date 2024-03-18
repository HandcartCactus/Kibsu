from lxml import etree
from typing import Dict
from .base import Resolver


class AllSubResolvers(metaclass=Resolver):
    def __init__(self, resolvers: Dict[str, Resolver]):
        self.resolvers = resolvers
        self.include = True
        self.resolver_type = 'AllSubResolvers'

    def debug(self, element: etree._Element):
        debug = super().debug(element)
        debug['subresolvers'] = {resolver_name: resolver.debug(element) for resolver_name, resolver in self.resolvers.items()}
        return debug
    
    def does_resolve(self, element: etree._Element):
        return all(resolver.does_resolve(element) for resolver in self.resolvers.values())
    
    def resolve(self, element: etree._Element):
        return {resolver_name: resolver.resolve(element) for resolver_name, resolver in self.resolvers.items() if resolver.include}