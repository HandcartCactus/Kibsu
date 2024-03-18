from .base import Resolver
from lxml import etree
from typing import List, Any

class XPathResolver(metaclass=Resolver):
    def __init__(self, xpath:str, include:bool=True):
        self.xpath = xpath
        self.include = include
        self.resolver_type = 'XPathResolver'

    def resolve(self, element: etree._Element) -> Any:
        #print(self.xpath, etree.tostring(element, encoding='unicode', method='html'))
        return element.xpath(self.xpath)
    
    def does_resolve(self, element: etree._Element) -> bool:
        return self.resolve(element) is not None