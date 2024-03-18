from typing import List
from .base import Resolver
from .function_resolver import FunctionResolver
from .any_subresolver import AnySubResolvers
from .one_subresolver import OneSubResolver
from lxml import etree
from datetime import datetime

def parser_for_date_format(date_format:str):
    def date_parser(element: etree._Element):
        return datetime.strptime((element.text or '').strip(), date_format)
    return date_parser

def date_format_to_iso_parser(date_format:str):
    def date_parser(element: etree._Element):
        return datetime.strptime((element.text or '').strip(), date_format).isoformat()
    return date_parser

def date_resolver_factory(format:str, resolve_iso_format:bool=True):
    parser_func = date_format_to_iso_parser if resolve_iso_format else parser_for_date_format
    return FunctionResolver(parser_func(format))

def multiformat_date_resolver_factory(formats:List[str], resolve_iso_format:bool=True, mutually_exclusive:bool=False):
    resolver_logic = OneSubResolver if mutually_exclusive else AnySubResolvers
    return resolver_logic(
        resolvers={
            fmt: date_resolver_factory(
                fmt, 
                resolve_iso_format=resolve_iso_format
            ) for fmt in formats
        }
    )


