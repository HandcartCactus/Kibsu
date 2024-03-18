from lxml import etree
from .base import Resolver
    
class InverseResolver(metaclass=Resolver):
    def __init__(self, resolver: Resolver):
        self.resolver = resolver
        self.include = False
        self.resolver_type = 'InverseResolver'

    def does_resolve(self, element: etree._Element) -> bool:
        return not self.resolver.resolve(element)
    def resolve(self, element: etree._Element) -> None:
        return None
    def debug(self, element: etree._Element):
        debug = super().debug(element)
        debug['inverse_of'] = self.resolver.debug()
        return debug