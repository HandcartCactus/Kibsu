from lxml import etree
from typing import Dict
from .base import Resolver

class ShallowestResolver(metaclass=Resolver):
    def __init__(self, resolvers: Dict[str, Resolver], parent_only:bool=True):
        self.resolvers = resolvers
        self.parent_only = parent_only
        self.include = True
        self.resolver_type= 'ShallowestResolver'
    
    def does_resolve(self, element: etree._Element):
        this_element_does_resolve = all(resolver.does_resolve(element) for resolver in self.resolvers.values())
        first_to_resolve = True
        if self.parent_only:
            first_to_resolve = all(resolver.does_resolve(element.getparent()) for resolver in self.resolvers.values())
        else:
            for ancestor in element.iterancestors():
                does_resolve = all(resolver.does_resolve(ancestor) for resolver in self.resolvers.values())
                if does_resolve:
                    first_to_resolve = False
                    break
        
        return this_element_does_resolve and first_to_resolve
    
    def resolve(self, element: etree._Element):
        return {resolver_name: resolver.resolve(element) for resolver_name, resolver in self.resolvers.items() if resolver.include}
    
    def debug(self, element: etree._Element):
        debug = super().debug(element)
        debug['subresolvers'] = {resolver_name: resolver.debug(element) for resolver_name, resolver in self.resolvers.items()}
        debug['parent_only'] = self.parent_only
        return debug