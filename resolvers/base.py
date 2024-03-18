from abc import ABCMeta, abstractmethod
from typing import Any
from lxml import etree


class Resolver(ABCMeta):

    @abstractmethod
    def does_resolve(self, element: etree._Element) -> bool:
        ...
    
    @abstractmethod
    def resolve(self, element: etree._Element) -> Any:
        ...

    def debug(self, element: etree._Element):
        return {
            'resolver_type': self.resolver_type,
            'does_resolve': self.does_resolve(element),
            'resolve': self.resolve(element),
            'include': self.include,
        }

    
    @property
    @abstractmethod
    def include(self) -> bool:
        pass

    @property
    @abstractmethod
    def resolver_type(self) -> str:
        ...