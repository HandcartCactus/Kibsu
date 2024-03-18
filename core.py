from lxml import etree
from typing import List, Any, Dict, Mapping
from resolvers.base import Resolver

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
            raise Warning(f'The key {pi} does not exist in {current}.')
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