# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project
# vim: tw=120 ts=4 et

# Node types representing an Android Interface Definition Language (AIDL) AST.
# Similar in structure like ifex_ast.py and others

from dataclasses import dataclass, field
from typing import List, Optional, Union

# Examples of input are shown in the docstrings.

@dataclass
class Import:
    """Example: import com.example.Foo;"""
    path: str


@dataclass
class EnumElement:
    """A single value inside an AIDL enum."""
    name: str
    value: Optional[str] = None


@dataclass
class Enum:
    """Example: enum Status { OK = 0, ERR = 1 }"""
    name: str
    elements: Optional[List[EnumElement]] = None


@dataclass
class Parameter:
    """A method parameter with an explicit direction annotation."""
    name: str
    datatype: str
    direction: str = "in"   # "in" | "out" | "inout"


@dataclass
class Method:
    """A method declared inside an AIDL interface."""
    name: str
    return_type: str          # "void" or a type name
    parameters: Optional[List[Parameter]] = None
    oneway: bool = False


@dataclass
class Const:
    """Example: const int MAX_VALUE = 100;"""
    name: str
    datatype: str
    value: str


@dataclass
class Interface:
    """Example: interface IFoo { ... }"""
    name: str
    methods: Optional[List[Method]] = None
    consts: Optional[List[Const]] = None
    oneway: bool = False      # True → all methods are oneway


@dataclass
class ParcelableField:
    """A field inside a parcelable data class."""
    name: str
    datatype: str


@dataclass
class Parcelable:
    """Example: parcelable Foo { ... }"""
    name: str
    fields: Optional[List[ParcelableField]] = None


@dataclass
class AIDLFile:
    """AIDL source file
    Each file is expected to have a package declaration, zero or more imports,
    and one top-level declaration (interface, parcelable, or enum)
    """
    package: str
    declaration: Union[Interface, Parcelable, Enum]
    imports: Optional[List[Import]] = None

    @property
    def filename(self) -> str:
        return self.declaration.name + ".aidl"
