from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import typing
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
    error: Optional[List[Error]] = None
    input: Optional[List[Argument]] = None
    output: Optional[List[Argument]] = None


@dataclass
class Event:
    name: str
    description: Optional[str] = None
    input: Optional[List[Argument]] = None


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


@dataclass
class Struct:
    name: str
    # TODO: do we need type field in a struct?
    type: Optional[str] = None
    description: Optional[str] = None
    members: Optional[List[Member]] = None


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
    namespaces: Optional[List['Namespace']] = None


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


# The item name (if available) is useful in debug and error messages
def _get_name(item):
    if isinstance(item, dict):
        return f" '{item.get('name', '')}' "
    else:
        return " "

def _actual_type(field):

    # Unpack type inside Optional (which is typed as Union)
    if typing.get_origin(field) == typing.Union:
        return typing.get_args(field)[0]

    # FIXME: ForwardRef check is not working this way
    elif typing.get_origin(field) == typing.ForwardRef:
        print("ForwardRef ")
        # Other idea: but __forward_arg__ is only there if it's a ForwardRef
        try:
            print(f"FWDARG:{field.__forward_arg__}")
        except:
            pass
        return typing.get_args(field)[0]

    else:
        return field

# Answer the question if AST field and/or YAML is a list type (and report
# mismatch).
def _is_list(class_name, name, dictionary):
    if typing.get_origin(_actual_type(class_name)) is list:
        #print(f"IS LIST {_actual_type(class_name)}")
        if isinstance(dictionary, (tuple, list)):
            return True
        else:
            print(f"\n**!!**\nERROR: Expected a list of objects for {class_name} {name}, but a single object was provided.")
            return False # Should probably throw exception here instead?
    else:
        #print(f"IS NOT LIST {_actual_type(class_name)}")
        if isinstance(dictionary, (tuple, list)):
            print(f"\n**!!**\nERROR: Expected a single object for {class_name} {name}, but a list was provided.")
            return True # Should probably throw exception here instead?
        else:
            return False

def parse_dataclass_from_dict(class_name, dictionary):

    # Name of item (for error/debug messages only)
    node_name = _get_name(dictionary)

    #print(f"parse_dataclass_from_dict() extracting node{node_name}of type {class_name}")

    # Is the field Optional[type] ?  Then we need to extract the inner type
    if typing.get_origin(class_name) == typing.Union:
        #print(f"+++ parse_dataclass_from_dict(): Handling Optional/Union: {class_name}")
        actual_type = typing.get_args(class_name)[0]
        #print(f"+++ Recursing with {actual_type}")
        return parse_dataclass_from_dict(actual_type, dictionary)
    # Is the YAML input a collection type?
    # => Then parse each item and return a list of the result
    elif _is_list(class_name, node_name, dictionary):
        #print(f"+++yaml node is of collection type: {type(dictionary)} for the class_name {class_name}?")
        return [parse_dataclass_from_dict( class_name.__args__[0], f) for f in dictionary]
    # Is the field *not* an AST type (it is a plain str or int)
    # => Then copy from YAML-dict directly -> no further recursion necessary
    # (TODO: Maybe some sanity-checking of the YAML input here.  Otherwise
    # it will not be noticed until code-generation.)
    elif class_name in (int, str, float):
        #print(f"!$#@ type is {class_name}")
        #print(f"!$#@ dictionary type is {type(dictionary)}")
        return dictionary

    # Finally, we assume class is a complex node (AST node)
    # => Recursive call to parch each field in the class
    #    and create an instance of the class using the instantiated fields
    else:
        #print(f"dataclass {class_name} actual {_actual_type(class_name)}")
        field_types = _actual_type(class_name).__annotations__

        fields = {}
        parent_name = node_name
        for key, item in dictionary.items():
            # Remember this for later printout
            try:
                subtype = field_types[key]
            except KeyError:
                print(f"\n**!!**\nERROR: Unexpected entry '{key}:' near object{parent_name}. It does not fit into type {class_name}")
                return None

            # Get name of item for error/debug messages only.
            node_name = _get_name(item)

            #print(f"rse_dataclass_from_dict() extracting node{node_name}of type {class_name}")
            #print(f"Extracting field: {key} {name} of type {subtype}")
            #print(f"NODE: {item}")
            try:
                fields[key] = parse_dataclass_from_dict(subtype, item)
            except AttributeError as e:
                print(f"\n**!!**\nERROR: Failed to extract data for '{key}' near object{parent_name} of type {class_name}.")
                print(str(e))
                fields[key] = None

        return class_name(**fields)

    ## This should not happen...
    if isinstance(dictionary, dict):
        print(f"***\n***\n*** DICT returned {class_name} {parent_name}")

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
    return parse_dataclass_from_dict(AST, ast_dict)


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
