from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import yaml


@dataclass
class Argument:
    name: str
    datatype: str
    description: Optional[str] = None
    arraysize: Optional[str] = None
    range: Optional[str] = None


@dataclass
class Error:
    datatype: str
    description: Optional[str] = None
    arraysize: Optional[str] = None
    range: Optional[str] = None
    description: Optional[str]= None


@dataclass
class Method:
    name: str
    description: Optional[str] = None
    errors: Optional[List[Error]] = None
    input: Optional[List[Argument]] = None
    output: Optional[List[Argument]] = None

    def __post_init__(self):
        if self.error is not None:
            self.error = [Error(**e) if isinstance(e, dict) else e for e in self.error]
        if self.input is not None:
            self.input = [Argument(**a) if isinstance(a, dict) else a for a in self.input]
        if self.output is not None:
            self.output = [Argument(**a) if isinstance(a, dict) else a for a in self.output]


@dataclass
class Event:
    name: str
    description: Optional[str] = None
    input: Optional[List[Argument]] = None

    def __post_init__(self):
        if self.input is not None:
            self.input = [Argument(**a) if isinstance(a, dict) else a for a in self.input]


@dataclass
class Property:
    name: str
    datatype: str
    description: Optional[str] = None
    arraysize: Optional[int] = None


@dataclass
class Member:
    name: str
    datatype: str
    description: Optional[str] = None
    arraysize: Optional[str] = None


@dataclass
class Option:
    name: str
    value: str
    description: Optional[str] = None


@dataclass
class Enumeration:
    name: str
    datatype: str
    options: List[Option]
    description: Optional[str] = None

    def __post_init__(self):
        if self.options is not None:
            self.options = [Option(**o) if isinstance(o, dict) else o for o in self.options]


@dataclass
class Struct:
    name: str
    # TODO: do we need type field in a struct?
    type: Optional[str] = None
    description: Optional[str] = None
    members: Optional[List[Member]] = None

    def __post_init__(self):
        if self.members is not None:
            self.members = [Member(**m) if isinstance(m, dict) else m for m in self.members]


@dataclass
class Typedef:
    name: str
    datatype: str
    description: Optional[str] = None
    arraysize: Optional[int] = None
    min: Optional[int] = None
    max: Optional[int] = None


@dataclass
class Include:
    file: str
    description: Optional[str] = None


@dataclass
class Namespace:
    name: str
    description: Optional[str] = None
    major_version: Optional[int] = None
    minor_version: Optional[int] = None
    events: Optional[List[Event]] = None
    methods: Optional[List[Method]] = None
    typedefs: Optional[List[Typedef]] = None
    includes: Optional[List[Include]] = None
    structs: Optional[List[Struct]] = None
    enumerations: Optional[List[Enumeration]] = None
    properties: Optional[List[Property]] = None
    namespaces: Optional[List[Namespace]] = None

    def __post_init__(self):
        if self.properties is not None:
            self.properties = [Property(**p) if isinstance(p, dict) else p for p in self.properties]
        if self.events is not None:
            self.events = [Event(**e) if isinstance(e, dict) else e for e in self.events]
        if self.methods is not None:
            self.methods = [Method(**m) if isinstance(m, dict) else m for m in self.methods]
        if self.includes is not None:
            self.includes = [Include(**i) if isinstance(i, dict) else i for i in self.includes]
        if self.structs is not None:
            self.structs = [Struct(**s) if isinstance(s, dict) else s for s in self.structs]
        if self.typedefs is not None:
            self.typedefs = [Typedef(**t) if isinstance(t, dict) else t for t in self.typedefs]
        if self.enumerations is not None:
            self.enumerations = [Enumeration(**e) if isinstance(e, dict) else e for e in self.enumerations]
        if self.namespaces is not None:
            self.namespaces = [Namespace(**n) if isinstance(n, dict) else n for n in self.namespaces]

#@dataclass
#class Service:
#    name: str
#    minor_version: int
#    major_version: int
#    description: str
#    namespaces: Optional[List[Namespace]] = None
#    description: Optional[str] = None


@dataclass
class AST:
    name: str
    minor_version: int
    major_version: int
    includes: Optional[List[Include]] = None
    namespaces: Optional[List[Namespace]] = None
    description: Optional[str] = None


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
    TODO: can have performance implications when file size is big. We have to consider incremental yaml processing.
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


def parse_ast_from_dict(ast_dict: Dict[Any, Any]) -> Namespace:
    """
    Tries to parse dictionary and create abstract syntax tree
    :param ast_dict: dictionary containing AST (vehicle service catalog)
    :return: AST
    """
    return parse_dataclass_from_dict(Namespace, ast_dict)


def read_ast_from_yaml_file(filename: str) -> Namespace:
    """
    Reads a yaml file and returns AST
    :param filename: path to a yaml file
    :return: abstract syntax tree (vehicle service catalog)
    """

    yaml_string = read_yaml_file(filename)

    yaml_dict = parse_yaml_file(yaml_string)

    ast = parse_ast_from_dict(yaml_dict)

    return ast
