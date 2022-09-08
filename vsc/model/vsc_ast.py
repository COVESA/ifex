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
    description: str = str()
    arraysize: Optional[str] = None
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
    error: List[Error] = field(default_factory=EmptyList)
    input: List[Argument] = field(default_factory=EmptyList)
    output: List[Argument] = field(default_factory=EmptyList)


@dataclass
class Event:
    name: str
    description: str = None
    input: List[Argument] = field(default_factory=EmptyList)


@dataclass
class Property:
    name: str
    datatype: str
    description: str = str()
    arraysize: Optional[int] = None


@dataclass
class Member:
    name: str
    datatype: str
    description: str = str()
    arraysize: Optional[str] = None


@dataclass
class Option:
    name: str
    value: int
    description: str = None


@dataclass
class Enumeration:
    name: str
    datatype: str
    options: List[Option]
    description: str = None


@dataclass
class Struct:
    name: str
    # TODO: do we need type field in a struct?
    type: Optional[str] = None
    description: str = str()
    members: List[Member] = field(default_factory=EmptyList)


@dataclass
class Typedef:
    name: str
    datatype: str
    description: str = str()
    arraysize: Optional[int] = None
    min: Optional[int] = None
    max: Optional[int] = None


@dataclass
class Include:
    file: str
    description: str = str()


@dataclass
class Namespace:
    name: str
    description: str = str()

    major_version: Optional[int] = None
    minor_version: Optional[int] = None

    events: List[Event] = field(default_factory=EmptyList)
    methods: List[Method] = field(default_factory=EmptyList)
    typedefs: List[Typedef] = field(default_factory=EmptyList)
    includes: List[Include] = field(default_factory=EmptyList)
    structs: List[Struct] = field(default_factory=EmptyList)
    enumerations: List[Enumeration] = field(default_factory=EmptyList)
    properties: List[Property] = field(default_factory=EmptyList)

    namespaces: List['Namespace'] = field(default_factory=EmptyList)


@dataclass
class AST(Namespace):
    pass
