# SPDX-FileCopyrightText: Copyright (c) 2022 MBition GmbH.
# All rights reserved.
# SPDX-License-Identifier: MPL-2.0

from dataclasses import dataclass, field
from typing import List, Optional


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

@dataclass
class AST(Namespace):
    pass

