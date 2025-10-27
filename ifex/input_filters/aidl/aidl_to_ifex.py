# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project
# vim: tw=120 ts=4 et

"""
Convert an AIDL AST (AIDLFile) to an IFEX AST (ifex.AST).

Public API:
    aidl_to_ifex(aidl_file: AIDLFile) -> ifex.AST

Follows the same approach as protobuf_to_ifex.py:
  - Manual tree-walking (no rule_translator)
  - Capitalised function names to make AST type names stand out
  - One conversion function per AIDL / IFEX type pair

Mapping summary
---------------
AIDL                        IFEX
----                        ----
AIDLFile.package        ->  Namespace.name  (full dotted name)
Interface               ->  ifex.Interface  (leading "I" stripped)
Method(oneway=False)    ->  ifex.Method
Method(oneway=True)     ->  ifex.Event
Parameter(dir="in")     ->  Argument in Method.input
Parameter(dir="out")    ->  Argument in Method.output
Method.return_type!="void" -> Argument in Method.returns
Parcelable              ->  ifex.Struct
ParcelableField         ->  ifex.Member
Enum                    ->  ifex.Enumeration (datatype="int32")
EnumElement             ->  ifex.Option
"""

import ifex.models.ifex.ifex_ast as ifex
from ifex.models.aidl.aidl_ast import (
    AIDLFile, Interface, Method, Parameter, Const,
    Parcelable, ParcelableField, Enum, EnumElement, Import,
)


# ============================================================
# Type translation  (reverse of ifex_to_aidl._type_map)
# ============================================================

_reverse_type_map = {
    "boolean": "boolean",
    "byte":    "uint8",
    "short":   "int16",
    "int":     "int32",
    "long":    "int64",
    "float":   "float",
    "double":  "double",
    "String":  "string",
    "IBinder": "opaque",
    "void":    "void",    # kept for internal use; not an IFEX type
}


def translate_type(t: str) -> str:
    """Map an AIDL type string to an IFEX type string.

    Array types (e.g. "int[]") are handled by stripping and reattaching
    the suffix.  Unknown types pass through unchanged.
    """
    if t.endswith("[]"):
        base = t[:-2]
        mapped = _reverse_type_map.get(base, base)
        return mapped + "[]"
    return _reverse_type_map.get(t, t)


# ============================================================
# Conversion helpers  (Capitalised names = AST types visible)
# ============================================================

def Params_to_Input(parameters) -> list:
    """Return 'in' (and 'inout') parameters as IFEX input Arguments."""
    if not parameters:
        return []
    return [ifex.Argument(name=p.name, datatype=translate_type(p.datatype))
            for p in parameters if p.direction in ('in', 'inout')]


def Params_to_Output(parameters) -> list:
    """Return 'out' (and 'inout') parameters as IFEX output Arguments."""
    if not parameters:
        return []
    return [ifex.Argument(name=p.name, datatype=translate_type(p.datatype))
            for p in parameters if p.direction in ('out', 'inout')]


def Method_to_Returns(method: Method):
    """If a method has a non-void return type, create a single returns Argument."""
    if method.return_type and method.return_type != 'void':
        return [ifex.Argument(name='_return', datatype=translate_type(method.return_type))]
    return []


def Methods_to_Methods(methods) -> list:
    """Convert non-oneway AIDL Methods to IFEX Methods."""
    result = []
    for m in (methods or []):
        if m.oneway:
            continue  # handled separately as Events
        input_args  = Params_to_Input(m.parameters)
        output_args = Params_to_Output(m.parameters)
        returns     = Method_to_Returns(m)
        result.append(ifex.Method(
            name    = m.name,
            input   = input_args  if input_args  else None,
            output  = output_args if output_args else None,
            returns = returns     if returns      else None,
        ))
    return result


def Methods_to_Events(methods) -> list:
    """Convert oneway AIDL Methods to IFEX Events."""
    result = []
    for m in (methods or []):
        if not m.oneway:
            continue
        input_args = Params_to_Input(m.parameters)
        result.append(ifex.Event(
            name  = m.name,
            input = input_args if input_args else None,
        ))
    return result


def Fields_to_Members(fields) -> list:
    """Convert Parcelable fields to IFEX Struct Members."""
    return [ifex.Member(name=f.name, datatype=translate_type(f.datatype))
            for f in (fields or [])]


def Elements_to_Options(elements) -> list:
    """Convert Enum elements to IFEX Options."""
    result = []
    for e in (elements or []):
        value = int(e.value) if e.value is not None else 0
        result.append(ifex.Option(name=e.name, value=value))
    return result


def Interface_to_Interface(aidl_iface: Interface) -> ifex.Interface:
    """Convert an AIDL Interface to an IFEX Interface.

    Strips the leading 'I' convention (IFoo -> Foo) to recover the
    original service name if present.
    """
    name = aidl_iface.name
    if name.startswith('I') and len(name) > 1 and name[1].isupper():
        name = name[1:]

    methods = Methods_to_Methods(aidl_iface.methods)
    events  = Methods_to_Events(aidl_iface.methods)

    return ifex.Interface(
        name    = name,
        methods = methods if methods else None,
        events  = events  if events  else None,
    )


def Parcelable_to_Struct(p: Parcelable) -> ifex.Struct:
    return ifex.Struct(
        name    = p.name,
        members = Fields_to_Members(p.fields) or None,
    )


def Enum_to_Enumeration(e: Enum) -> ifex.Enumeration:
    return ifex.Enumeration(
        name    = e.name,
        datatype = 'int32',
        options  = Elements_to_Options(e.elements),
    )


# ============================================================
# Main conversion entry point
# ============================================================

def aidl_to_ifex(aidl_file: AIDLFile) -> ifex.AST:
    """Convert an AIDLFile AST to an IFEX AST.

    A single AIDLFile becomes an AST with one Namespace whose name is
    the package from the AIDL file.  The single declaration becomes
    the appropriate IFEX construct within that Namespace.

    :param aidl_file: parsed AIDLFile AST
    :return: ifex.AST with one Namespace
    """
    declaration = aidl_file.declaration

    # Build the Namespace scaffold
    ns = ifex.Namespace(name=aidl_file.package)

    if isinstance(declaration, Interface):
        ns.interface = Interface_to_Interface(declaration)
    elif isinstance(declaration, Parcelable):
        ns.structs = [Parcelable_to_Struct(declaration)]
    elif isinstance(declaration, Enum):
        ns.enumerations = [Enum_to_Enumeration(declaration)]
    else:
        raise TypeError(f"Unknown AIDL declaration type: {type(declaration)}")

    return ifex.AST(namespaces=[ns])
