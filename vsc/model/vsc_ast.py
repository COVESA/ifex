# SPDX-FileCopyrightText: Copyright (c) 2022 MBition GmbH.
# All rights reserved.
# SPDX-License-Identifier: MPL-2.0

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import yaml, dacite


@dataclass
class Argument:
    name: str
    datatype: str
    description: Optional[str] = field(default_factory=lambda: str())
    arraysize: Optional[str] = None
    range: Optional[str] = None


@dataclass
class Error:
    datatype: str
    description: Optional[str] = field(default_factory=lambda: str())
    arraysize: Optional[str] = None
    range: Optional[str] = None


@dataclass
class Method:
    name: str
    description: Optional[str] = None
    error: Optional[List[Error]] = field(default_factory=lambda: [])
    input: Optional[List[Argument]] = field(default_factory=lambda: [])
    output: Optional[List[Argument]] = field(default_factory=lambda: [])


@dataclass
class Event:
    name: str
    description: Optional[str] = None
    input: Optional[List[Argument]] = field(default_factory=lambda: [])


@dataclass
class Property:
    name: str
    datatype: str
    description: Optional[str] = field(default_factory=lambda: str())
    arraysize: Optional[int] = None


@dataclass
class Member:
    name: str
    datatype: str
    description: Optional[str] = field(default_factory=lambda: str())
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
    description: Optional[str] = field(default_factory=lambda: str())
    members: Optional[List[Member]] = field(default_factory=lambda: [])


@dataclass
class Typedef:
    name: str
    datatype: str
    description: Optional[str] = field(default_factory=lambda: str())
    arraysize: Optional[int] = None
    min: Optional[int] = None
    max: Optional[int] = None


@dataclass
class Include:
    file: str
    description: Optional[str] = field(default_factory=lambda: str())


@dataclass
class Namespace:
    name: str
    description: Optional[str] = field(default_factory=lambda: str())

    major_version: Optional[int] = None
    minor_version: Optional[int] = None

    events: Optional[List[Event]] = field(default_factory=lambda: [])
    methods: Optional[List[Method]] = field(default_factory=lambda: [])
    typedefs: Optional[List[Typedef]] = field(default_factory=lambda: [])
    includes: Optional[List[Include]] = field(default_factory=lambda: [])
    structs: Optional[List[Struct]] = field(default_factory=lambda: [])
    enumerations: Optional[List[Enumeration]] = field(default_factory=lambda: [])
    properties: Optional[List[Property]] = field(default_factory=lambda: [])

    namespaces: Optional[List['Namespace']] = field(default_factory=lambda: [])


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
