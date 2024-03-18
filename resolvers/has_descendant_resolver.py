from lxml import etree
from typing import Dict
from .base import Resolver


class HasDescendantResolver(metaclass=Resolver):
    def __init__(self, resolvers: Dict[str, Resolver]):
        self.resolvers = resolvers
        self.include = True
        self.resolver_type = 'HasDescendantResolver'
    
    def does_resolve(self, element: etree._Element):
        resolving_descendants = False
        for subel in element.iterdescendants():
            if all(resolver.does_resolve(subel) for resolver in self.resolvers.values()):
                resolving_descendants = True
                break
        return resolving_descendants
    
    def resolve(self, element: etree._Element):
        resolving_descendants = False
        for subel in element.iterdescendants():
            if all(resolver.does_resolve(subel) for resolver in self.resolvers.values()):
                return {resolver_name: resolver.resolve(subel) for resolver_name, resolver in self.resolvers.items() if resolver.include}

    
    def debug(self, element: etree._Element):
        debug = super().debug(element)
        debug['subresolvers'] = {resolver_name: resolver.debug(element) for resolver_name, resolver in self.resolvers.items()}
        debug['children_only'] = self.children_only
        return debug