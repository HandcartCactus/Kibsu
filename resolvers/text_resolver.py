from .base import Resolver
from lxml import etree
from typing import List, Any

class TextResolver(metaclass=Resolver):
    def __init__(self, include:bool=True):
        self.include = include
        self.resolver_type = 'TextResolver'

    def _get_text(self, element: etree._Element)-> List[etree._Element]:
        return '\n'.join([e.strip() for e in element.xpath(".//text()")])

    def resolve(self, element: etree._Element) -> Any:
        return {'text': self._get_text(element).strip()}
    
    def does_resolve(self, element: etree._Element) -> bool:
        return len(self._get_text(element).strip()) > 0