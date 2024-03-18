from lxml import etree
from typing import Dict
from .base import Resolver


class DeepestResolver(metaclass=Resolver):
    def __init__(self, resolvers: Dict[str, Resolver], children_only:bool=True):
        self.resolvers = resolvers
        self.children_only = children_only
        self.include = True
        self.resolver_type = 'DeepestResolver'
    
    def does_resolve(self, element: etree._Element):
        this_element_does_resolve = all(resolver.does_resolve(element) for resolver in self.resolvers.values())
        last_to_resolve = True
        subelements_to_check = element.iterchildren() if self.children_only else element.iterdescendants()
        for subel in subelements_to_check:
            deeper_does_resolve = all(resolver.does_resolve(subel) for resolver in self.resolvers.values())
            if deeper_does_resolve:
                last_to_resolve = False
                break
        
        return this_element_does_resolve and last_to_resolve
    
    def resolve(self, element: etree._Element):
        return {resolver_name: resolver.resolve(element) for resolver_name, resolver in self.resolvers.items() if resolver.include}
    
    def debug(self, element: etree._Element):
        debug = super().debug(element)
        debug['subresolvers'] = {resolver_name: resolver.debug(element) for resolver_name, resolver in self.resolvers.items()}
        debug['children_only'] = self.children_only
        return debug