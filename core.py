from lxml import etree
import requests
from typing import List, Protocol, Any, Dict, Mapping
from abc import ABC, abstractmethod, abstractproperty, ABCMeta
from datetime import datetime
from pprint import pprint

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


class AllSubResolvers(metaclass=Resolver):
    def __init__(self, resolvers: Dict[str, Resolver]):
        self.resolvers = resolvers
        self.include = True
        self.resolver_type = 'AllSubResolvers'

    def debug(self, element: etree._Element):
        debug = super().debug(element)
        debug['subresolvers'] = {resolver_name: resolver.debug(element) for resolver_name, resolver in self.resolvers.items()}
        return debug
    
    def does_resolve(self, element: etree._Element):
        return all(resolver.does_resolve(element) for resolver in self.resolvers.values())
    
    def resolve(self, element: etree._Element):
        return {resolver_name: resolver.resolve(element) for resolver_name, resolver in self.resolvers.items() if resolver.include}
    
class AnySubResolvers(metaclass=Resolver):
    def __init__(self, resolvers: Dict[str, Resolver]):
        self.resolvers = resolvers
        self.include = True
        self.resolver_type = 'AnySubResolvers'

    def debug(self, element: etree._Element):
        debug = super().debug(element)
        debug['subresolvers'] = {resolver_name: resolver.debug(element) for resolver_name, resolver in self.resolvers.items()}
        return debug
    
    def does_resolve(self, element: etree._Element):
        return any(resolver.does_resolve(element) for resolver in self.resolvers.values())
    
    def resolve(self, element: etree._Element):
        return {resolver_name: resolver.resolve(element) for resolver_name, resolver in self.resolvers.items() if resolver.does_resolve(element) and resolver.include}


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
            
class NoSubResolvers(metaclass=Resolver):
    def __init__(self, resolvers: Dict[str, Resolver]):
        self.resolvers = resolvers
        self.include = False
        self.resolver_type = 'NoSubResolvers'
    
    def does_resolve(self, element: etree._Element):
        return all(not resolver.does_resolve(element) for resolver in self.resolvers.values())
    
    def resolve(self, element: etree._Element):
        #raise ValueError('The type NoResolvers does not support resolving. If `resolver.include==False`, you cannot call resolver.resolve().')
        return None
    
    def debug(self, element: etree._Element):
        debug = super().debug(element)
        debug['subresolvers'] = {resolver_name: resolver.debug(element) for resolver_name, resolver in self.resolvers.items()}
        return debug
    
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
    
class OptionalResolver(metaclass=Resolver):
    def __init__(self, resolvers: Dict[str, Resolver]):
        self.resolvers = resolvers
        self.include = True
        self.resolver_type= 'OptionalResolver'
    
    def does_resolve(self, element: etree._Element):
        return True
    
    def resolve(self, element: etree._Element):
        return {resolver_name: resolver.resolve(element) for resolver_name, resolver in self.resolvers.items() if resolver.does_resolve(element) and resolver.include}
    
    def debug(self, element: etree._Element):
        debug = super().debug(element)
        debug['subresolvers'] = {resolver_name: resolver.debug(element) for resolver_name, resolver in self.resolvers.items()}
        return debug
    
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
    
def parser_for_date_format(date_format:str):
    def date_parser(element: etree._Element):
        return datetime.strptime((element.text or '').strip(), date_format)
    return date_parser

def date_format_to_iso_parser(date_format:str):
    def date_parser(element: etree._Element):
        return datetime.strptime((element.text or '').strip(), date_format).isoformat()
    return date_parser


class FlatMapper:
    def __init__(self, key_to_path:Mapping[str, List[str]]) -> None:
        self.key_to_path = key_to_path
    
    def __call__(self, nested_dict:Dict[str, Any]):
        flat_mapped = {}
        try:
            for key, path in self.key_to_path.items():
                current = nested_dict
                for pi in path:
                    current = current[pi]
                flat_mapped[key] = current
        except KeyError as e:
            pprint(current)
            print(f'has no key {pi}.')
        return flat_mapped

    


class Kibsu:
    def __init__(self, resolvers: Dict[str, Resolver]):
        self.resolvers = resolvers
    
    def generate_resolutions(self, etree: etree._ElementTree):
        
        for descendant in etree.iter():
            if all(resolver.does_resolve(descendant) for resolver_name, resolver in self.resolvers.items()):
                yield {resolver_name: resolver.resolve(descendant) for resolver_name, resolver in self.resolvers.items() if resolver.include}

    def __call__(self, etree: etree._ElementTree):
        return list(self.generate_resolutions(etree))

    
if __name__ == '__main__':


    has_descendant_with_link = HasDescendantResolver(
        {
            'link': LinkOrFragmentResolver(),
        }
    )
    
    has_descendant_with_date = HasDescendantResolver(
        resolvers = {
            'pub_date': OneSubResolver(
                resolvers = {
                    '%B %d, %Y': FunctionResolver(date_format_to_iso_parser('%B %d, %Y')),
                    '%m/%d/%y': FunctionResolver(date_format_to_iso_parser('%m/%d/%y')),
                    '%A, %B %d, %Y': FunctionResolver(date_format_to_iso_parser('%A, %B %d, %Y')),
                }
            ),
        },
    )

    get_press_releases = Kibsu(
        resolvers = {
            'press_release': DeepestResolver(
                resolvers = {
                    'link_descendant': has_descendant_with_link,
                    'date_descendant': has_descendant_with_date,
                },
                children_only=True
            ),
        }
    )

    press_release_urls = [
        'https://www.markey.senate.gov/news/press-releases',
        'https://www.young.senate.gov/newsroom/press-releases/',
        'https://www.mcconnell.senate.gov/public/index.cfm/pressreleases',
        'https://www.crapo.senate.gov/media/newsreleases',
        'https://www.wyden.senate.gov/news/blog',
    ]

    for url in press_release_urls:
        print(url)
        r = requests.get(url)
        tree = etree.ElementTree(etree.HTML(r.content))
        press_releases = get_press_releases(tree)
        #pprint(press_releases[2])
        flat_mapper = FlatMapper({
            'date': ['press_release', 'date_descendant', 'pub_date'],
            'link_url': ['press_release', 'link_descendant', 'link', 'url'],
            'link_text': ['press_release', 'link_descendant', 'link', 'text'],
        })
        pprint(flat_mapper(press_releases[2]))