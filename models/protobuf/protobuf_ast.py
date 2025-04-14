# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project

# Node types to represent a Protobuf AST, similar to ifex_ast.py

from dataclasses import dataclass
from typing import List, Optional, Union

@dataclass
class StructuredOption:
    name: str
    value: str

# The protobuf syntax is different for options when they appear in
# rpc/service/msg or in fields, but the actual content is the same
# However, it helps output-templates if the types are different, so
# they can generate different output
# For now FieldOption is treated separate - may be needed also for others
@dataclass
class Option:
    name: str
    # NOTE: An option is *either* one value, or a list of structuredoption values
    value: Optional[str] = None
    structuredoptions: Optional[List[StructuredOption]] = None

@dataclass
class FieldOption:
    name: str
    value: str

@dataclass
class EnumField:
    name: str
    value: str
    options: Optional[List[FieldOption]] = None

@dataclass
class MapField:
    name: str
    keytype: str
    valuetype: str
    options: Optional[List[FieldOption]] = None

@dataclass
class Field:
    name: str
    datatype: str
    repeated: Optional[bool] = False
    optional: Optional[bool] = False
    options: Optional[List[FieldOption]] = None

@dataclass
class OneOf:
    name: str
    options: Optional[List[Option]]
    # Note: Strictly speaking OneOf does not accept a normal field type because
    # a normal field can have "repeated" keyword, which does not fit here.
    # For the purpose of this definition, we leave that slight possibility as
    # it is and accept the common Field definition here.
    fields: List[Field]

@dataclass
class Import:
    path: str
    # Note: Only one of weak or public can be true
    weak: Optional[bool] = False
    public: Optional[bool] = False

@dataclass
class Range:
    single_value: Optional[str]
    range_start: Optional[int]
    range_end: Optional[Union[int, str]] # str would be set to "max"

@dataclass
class Reserved:
    ranges: Optional[List[Range]] = None
    strfieldnames: Optional[List[str]] = None

@dataclass
class Enumeration:
    name: str
    fields: List[EnumField] = None
    options: Optional[List[Option]] = None
    reservations: Optional[List[Reserved]] = None

@dataclass
class Message:
    name: str
    enums: Optional[List[Enumeration]] = None
    fields: Optional[List[Field]] = None
    messages: Optional[List["Message"]] = None
    options: Optional[List[Option]] = None
    oneofs: Optional[List[OneOf]] = None
    mapfields: Optional[List[MapField]] = None
    reservations: Optional[List[Reserved]] = None

@dataclass
class RPC:
    name: str
    input: Optional[str] = None   # _Reference_ to a Message (not defining a NEW Message)
    input_stream: Optional[bool] = False
    returns: Optional[str] = None # (same as above)
    return_stream: Optional[bool] = False
    options: Optional[List[Option]] = None

@dataclass
class Service:
    name: str
    rpcs: List[RPC]
    options: Optional[List[Option]] = None

# Proto = top level root of the tree:
@dataclass
class Proto:
    # NOTE! The grammar in the protobuf specification grammar allows MULTIPLE
    # package statements - but it is not clear that this is valid.  If it is is
    # the order and position in the file relevant?  The spec uses singular
    # words when describing: quote: "The package specifier can be used to
    # prevent name clashes between protocol message types".  For now, we limit
    # it to one, and the parser will otherwise warn.
    package: Optional[str] = None
    imports: Optional[List[Import]] = None
    options: Optional[List[Option]] = None
    messages: Optional[List[Message]] = None
    enums: Optional[List[Enumeration]] = None
    services: Optional[List[Service]] = None
    #syntax: not used (always = 'proto3' anyway)
