from lxml import etree
from typing import Protocol, Any
from .base import Resolver

class ElementFunction(Protocol):
    def __call__(self, element: etree._Element, *args, **kwargs) -> Any:
        ...

class FunctionResolver(metaclass=Resolver):
    def __init__(self, function: ElementFunction) -> None:
        self.function = function
        self.include = True,
        self.resolver_type = 'FunctionResolver'

    def does_resolve(self, element: etree.Element) -> bool:
        does_resolve = False

        try:
            if self.function(element) is not None:
                does_resolve = True
        except Exception as e:
            pass

        return does_resolve
    
    def resolve(self, element: etree.Element) -> Any:
        return self.function(element)
    
    def debug(self, element: etree._Element):
        debug = super().debug(element)
        debug['function_name'] = self.function.__qualname__
        return debug