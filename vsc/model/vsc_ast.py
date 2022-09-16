# SPDX-FileCopyrightText: Copyright (c) 2022 MBition GmbH.
# All rights reserved.
# SPDX-License-Identifier: MPL-2.0

from dataclasses import dataclass, field
from typing import List, Optional

# shortcut to reduce code duplication for default_factory 
# parameter in field()
EmptyList = lambda: []

@dataclass
class Argument:
    name: str
    datatype: str 
    description: Optional[str] = str()
    arraysize: Optional[int] = None
    range: Optional[str] = None


@dataclass
class Error:
    datatype: str
    description: Optional[str] = str()
    arraysize: Optional[str] = None
    range: Optional[str] = None


@dataclass
class Method:
    name: str
    description: Optional[str] = None
    error: Optional[List[Error]] = field(default_factory=EmptyList)
    input: Optional[List[Argument]] = field(default_factory=EmptyList)
    output: Optional[List[Argument]] = field(default_factory=EmptyList)


@dataclass
class Event:
    name: str
    description: Optional[str] = str()
    input: Optional[List[Argument]] = field(default_factory=EmptyList)


@dataclass
class Property:
    name: str
    datatype: str
    description: Optional[str] = str()
    arraysize: Optional[int] = None


@dataclass
class Member:
    name: str
    datatype: str
    description: Optional[str] = str()
    arraysize: Optional[int] = None


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
    description: Optional[str] = str()
    members: Optional[List[Member]] = field(default_factory=EmptyList)


@dataclass
class Typedef:
    name: str
    datatype: str
    description: Optional[str] = str()
    arraysize: Optional[int] = None
    min: Optional[int] = None
    max: Optional[int] = None


@dataclass
class Include:
    file: str
    description: Optional[str] = str()


@dataclass
class Namespace:
    name: str
    description: Optional[str] = str()

    major_version: Optional[int] = None
    minor_version: Optional[int] = None

    events: Optional[List[Event]] = field(default_factory=EmptyList)
    methods: Optional[List[Method]] = field(default_factory=EmptyList)
    typedefs: Optional[List[Typedef]] = field(default_factory=EmptyList)
    includes: Optional[List[Include]] = field(default_factory=EmptyList)
    structs: Optional[List[Struct]] = field(default_factory=EmptyList)
    enumerations: Optional[List[Enumeration]] = field(default_factory=EmptyList)
    properties: Optional[List[Property]] = field(default_factory=EmptyList)

    namespaces: Optional[List['Namespace']] = field(default_factory=EmptyList)


@dataclass
class AST(Namespace):
    pass
