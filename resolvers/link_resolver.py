from .base import Resolver
from lxml import etree
from typing import List, Any

class LinkResolver(metaclass=Resolver):
    def __init__(self, include:bool=True):
        self.include = include
        self.resolver_type = 'LinkResolver'

    def _get_link_elements(self, element: etree._Element)-> List[etree._Element]:
        return element.xpath("self::node()[@href and starts-with(@href, 'http://') or starts-with(@href, 'https://')]")

    def resolve(self, element: etree._Element) -> Any:
        #print(self.xpath, etree.tostring(element, encoding='unicode', method='html'))
        #etree._Element().
        first_link = self._get_link_elements(element)[0]
        link_text = first_link.text or ''
        return {'url': first_link.attrib['href'], 'text': link_text.strip()}
    
    def does_resolve(self, element: etree._Element) -> bool:
        return len(self._get_link_elements(element)) > 0
    
class LinkOrFragmentResolver(metaclass=Resolver):
    def __init__(self, include:bool=True):
        self.include = include
        self.resolver_type = 'LinkFragmentResolver'

    def _get_link_elements(self, element: etree._Element)-> List[etree._Element]:
        return element.xpath("self::node()[@href and starts-with(@href, '/') or starts-with(@href, 'https://') or starts-with(@href, 'http://')]")

    def resolve(self, element: etree._Element) -> Any:
        #print(self.xpath, etree.tostring(element, encoding='unicode', method='html'))
        #etree._Element().
        first_link = self._get_link_elements(element)[0]
        link_text = first_link.text
        if not link_text:
            link_text = ' '.join([e.strip() for e in first_link.xpath(".//text()")])
        if not link_text:
            link_text = ''
        
        return {'url': first_link.attrib['href'], 'text': link_text.strip()}
    
    def does_resolve(self, element: etree._Element) -> bool:
        return len(self._get_link_elements(element)) > 0