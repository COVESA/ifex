# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project
# vim: tw=120 ts=4 et

"""
Node types representing an OMG IDL (Object Management Group Interface
Definition Language) AST.  Mirrors the structure of aidl_ast.py /
protobuf_ast.py.

Reference specification: OMG IDL 4.2 (formal/2021-06-01)
https://www.omg.org/spec/IDL/4.2

Key structural differences from AIDL:
  - An IDL *file* may contain multiple top-level declarations (modules,
    interfaces, structs, enums, typedefs, etc.)  — no one-per-file rule.
  - Namespacing is done with `module` blocks (nestable), not `package`.
  - Interfaces support inheritance (single and multiple).
  - Operations may declare exceptions via `raises(...)`.
  - `attribute` / `readonly attribute` declares a property.
  - `exception` is a first-class named type (like a struct with semantics).
  - `typedef` creates type aliases.
  - `enum` values are *ordered names* — no explicit integer assignment.
  - `sequence<T>` is a variable-length collection type.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


# ============================================================
# Leaf / shared types
# ============================================================

@dataclass
class Member:
    """A field inside a struct or exception body.

    Spec §7.4.9 (struct), §7.4.15 (exception)::

        member ::= type_spec declarators ";"
    """
    name: str
    datatype: str


@dataclass
class Parameter:
    """A parameter in an operation signature.

    Spec §7.4.12 (op_param_attribute)::

        param_dcl ::= param_attribute simple_type_spec declarator
        param_attribute ::= "in" | "out" | "inout"
    """
    name: str
    datatype: str
    direction: str = "in"   # "in" | "out" | "inout"


@dataclass
class Enumerator:
    """A single enumerator inside an enum.

    Spec §7.4.14::

        enum_type ::= "enum" identifier "{" enumerator {"," enumerator} "}"
        enumerator ::= identifier
    """
    name: str


@dataclass
class Const:
    """A named constant.

    Spec §7.4.4::

        const_dcl ::= "const" const_type identifier "=" const_exp
    """
    name: str
    datatype: str
    value: str


# ============================================================
# Constructed types
# ============================================================

@dataclass
class Struct:
    """An IDL struct (value type aggregate).

    Spec §7.4.9::

        struct_type ::= "struct" identifier "{" member+ "}"
    """
    name: str
    members: Optional[List[Member]] = None


@dataclass
class Enum:
    """An IDL enumeration.

    Spec §7.4.14::

        enum_type ::= "enum" identifier "{" enumerator {"," enumerator} "}"
    """
    name: str
    enumerators: Optional[List[Enumerator]] = None


@dataclass
class Exception_:
    """An IDL exception type.

    Named Exception_ to avoid collision with the Python built-in.

    Spec §7.4.15::

        except_dcl ::= "exception" identifier "{" member* "}"
    """
    name: str
    members: Optional[List[Member]] = None


@dataclass
class Typedef:
    """An IDL type alias.

    Spec §7.4.8::

        type_dcl ::= "typedef" type_declarator
        type_declarator ::= type_spec declarators
    """
    name: str
    datatype: str   # e.g. "long", "sequence<float>", "ClimateZone[3]"


# ============================================================
# Interface members
# ============================================================

@dataclass
class Operation:
    """An interface operation (method).

    Spec §7.4.12::

        op_dcl ::= [op_attribute] op_type_spec identifier
                   parameter_dcls [raises_expr]
        op_attribute ::= "oneway"
    """
    name: str
    return_type: str                        # "void" or a type name
    parameters: Optional[List[Parameter]] = None
    raises: Optional[List[str]] = None      # list of exception type names
    oneway: bool = False


@dataclass
class Attribute:
    """An interface attribute (property).

    Spec §7.4.13::

        attr_dcl ::= ["readonly"] "attribute" param_type_spec
                      simple_declarator {"," simple_declarator}
    """
    name: str
    datatype: str
    readonly: bool = False


@dataclass
class Interface:
    """An IDL interface definition.

    Spec §7.4.11::

        interface_dcl ::= interface_header "{" interface_body "}"
        interface_header ::= "interface" identifier [inheritance_spec]
        inheritance_spec ::= ":" scoped_name {"," scoped_name}
    """
    name: str
    inherits: Optional[List[str]] = None        # parent interface names (scoped)
    operations: Optional[List[Operation]] = None
    attributes: Optional[List[Attribute]] = None
    consts: Optional[List[Const]] = None


# ============================================================
# Module (namespace)
# ============================================================

@dataclass
class Module:
    """An IDL module (namespace scope).

    Modules may be nested and may be reopened (multiple blocks with the
    same name are merged).

    Spec §7.2.3::

        module_dcl ::= "module" identifier "{" definition+ "}"
    """
    name: str
    interfaces: Optional[List[Interface]] = None
    structs: Optional[List[Struct]] = None
    enums: Optional[List[Enum]] = None
    exceptions: Optional[List[Exception_]] = None
    typedefs: Optional[List[Typedef]] = None
    consts: Optional[List[Const]] = None
    modules: Optional[List[Module]] = None      # nested sub-modules


# ============================================================
# Top-level file
# ============================================================

@dataclass
class IDLFile:
    """Represents a single parsed .idl source file.

    Unlike AIDL, an IDL file may contain multiple top-level declarations
    (modules, interfaces, structs, etc.) without being wrapped in a module.
    """
    modules: Optional[List[Module]] = None
    # Top-level (outside any module) declarations:
    interfaces: Optional[List[Interface]] = None
    structs: Optional[List[Struct]] = None
    enums: Optional[List[Enum]] = None
    exceptions: Optional[List[Exception_]] = None
    typedefs: Optional[List[Typedef]] = None
    consts: Optional[List[Const]] = None
