from lxml import etree
from typing import Dict
from .base import Resolver


class OneSubResolver(metaclass=Resolver):
    def __init__(self, resolvers: Dict[str, Resolver]):
        self.resolvers = resolvers
        self.include = True
        self.resolver_type = 'OneSubResolver'

    def does_resolve(self, element: etree._Element):
        return sum(resolver.does_resolve(element) for resolver in self.resolvers.values()) == 1

    def resolve(self, element: etree._Element):
        for resolver_name, resolver in self.resolvers.items():
            if resolver.does_resolve(element) and resolver.include:
                return resolver.resolve(element)

    def debug(self, element: etree._Element):
        debug = super().debug(element)
        debug['subresolvers'] = {resolver_name: resolver.debug(element) for resolver_name, resolver in self.resolvers.items()}
        return debug