from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import yaml

@dataclass
class Argument:
    name: str
    description: str
    datatype: str
    array_size: Optional[str] = None
    range: Optional[str] = None


@dataclass
class Error:
    datatype: str
    array_size: Optional[str] = None
    range: Optional[str] = None


@dataclass
class Method:
    name: str
    description: str
    error: Error
    input: Optional[List[Argument]] = None
    output: Optional[List[Argument]] = None


@dataclass
class Event:
    name: str
    description: str
    output: Optional[List[Argument]] = None


@dataclass
class Property:
    name: str
    datatype: str
    description: Optional[str] = None
    array_size: Optional[int] = None


@dataclass
class Member:
    name: str
    description: str
    datatype: str
    array_size: Optional[str] = None


@dataclass
class Option:
    name: str
    value: str
    description: str


@dataclass
class Struct:
    name: str
    members: List[Member]
    description: Optional[str] = None


@dataclass
class Typedef:
    name: str
    description: str
    datatype: str
    array_size: Optional[int] = None
    min: Optional[int] = None
    max: Optional[int] = None


@dataclass
class Namespace:
    name: str
    description: Optional[str]
    major_version: Optional[int]
    minor_version: Optional[int]
    typedefs: Optional[List[Typedef]] = None


@dataclass
class Service:
    name: str
    description: str
    major_version: int
    minor_version: int
    namespaces: Optional[List[Namespace]] = None


@dataclass
class Include:
    file: str
    description: Optional[str] = None


@dataclass
class AST:
    service: Service
    includes: Optional[List[Include]] = None


def parse_dataclass_from_dict(class_name, dictionary):
    try:
        field_types = class_name.__annotations__
        return class_name(
            **{f: parse_dataclass_from_dict(field_types[f], dictionary[f]) for f in dictionary})
    except AttributeError:
        if isinstance(dictionary, (tuple, list)):
            return [
                parse_dataclass_from_dict(
                    class_name.__args__[0],
                    f) for f in dictionary]
        return dictionary


def read_yaml_file(filename) -> str:
    """
    Tries to read a file which contains yaml into a string
    TODO: can have performance implications when filesize is big. We have to consider incremental yaml processing.
    :param filename:
    :return: file contents as string
    """
    with open(filename, 'r') as yaml_file:
        return yaml_file.read()


def parse_yaml_file(yaml_string: str) -> Dict[Any, Any]:
    """
    Tries to parse yaml into a python dictionary
    :param yaml_string: String containing text in YAML format
    :return: Dictionary
    """
    return yaml.safe_load(yaml_string)


def parse_ast_from_dict(ast_dict: Dict[Any, Any]) -> AST:
    """
    Tries to parse dictionary and create abstract syntax tree
    :param ast_dict: dictionary containing AST (vehicle service catalog)
    :return: AST
    """
    return parse_dataclass_from_dict(AST, ast_dict)


def read_ast_from_yaml_file(filename: str) -> AST:
    """
    Reads a yaml file and returns AST
    :param filename: path to a yaml file
    :return: abstract syntax tree (vehicle service catalog)
    """

    yaml_string = read_yaml_file(filename)

    yaml_dict = parse_yaml_file(yaml_string)

    ast = parse_ast_from_dict(yaml_dict)

    return ast
