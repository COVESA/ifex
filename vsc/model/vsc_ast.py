# SPDX-FileCopyrightText: Copyright (c) 2022 MBition GmbH.
# All rights reserved.
# SPDX-License-Identifier: MPL-2.0

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import yaml, dacite


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
    value: int
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


def read_ast_from_yaml_file(filename: str) -> Namespace:
    """
    Reads a yaml file and returns AST
    :param filename: path to a yaml file
    :return: abstract syntax tree (vehicle service catalog)
    """

    yaml_string = read_yaml_file(filename)

    yaml_dict = parse_yaml_file(yaml_string)

    ast = dacite.from_dict(data_class=Namespace, data=yaml_dict)

    return ast
