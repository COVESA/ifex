# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project
# vim: tw=120 ts=4 et

"""
Functional transformation from IFEX AST to a list of AIDL AST nodes.

Each top-level IFEX declaration (Interface, Struct, Enumeration) becomes a
separate AIDLFile, matching AIDL's file-per-type convention.

IFEX → AIDL mapping:
  Namespace          → package name (string)
  Interface          → Interface  (.aidl file)
  Method (with output/returns) → Method (typed return, in/out params)
  Event              → Method(oneway=True, return_type="void")
  Argument (input)   → Parameter(direction="in")
  Argument (output)  → Parameter(direction="out")
  Struct             → Parcelable (.aidl file)
  Member             → ParcelableField
  Enumeration        → Enum       (.aidl file)
  Option             → EnumElement
  Property           → getter/setter Method pair inside the Interface
"""

import ifex.models.ifex.ifex_ast as ifex
from ifex.models.aidl.aidl_ast import (
    AIDLFile, Import, Interface, Method, Parameter,
    Parcelable, ParcelableField, Enum, EnumElement, Const,
)
from typing import List, Optional

# ---------------------------------------------------------------------------
# Type translation table: IFEX primitive types → AIDL types
# ---------------------------------------------------------------------------

_type_map = {
    "boolean": "boolean",
    "uint8":   "byte",
    "int8":    "byte",
    "uint16":  "int",      # AIDL has no unsigned; widen to int
    "int16":   "short",
    "uint32":  "int",      # lossy — no unsigned in AIDL
    "int32":   "int",
    "uint64":  "long",     # lossy
    "int64":   "long",
    "float":   "float",
    "double":  "double",
    "string":  "String",
    "uint8[]": "byte[]",
    "opaque":  "IBinder",
}


def translate_type(ifex_type: str) -> str:
    """Map an IFEX type name to the closest AIDL equivalent."""
    if ifex_type is None:
        return "void"
    # Handle array syntax: e.g. "int32[]" → "int[]"
    if ifex_type.endswith("[]"):
        base = ifex_type[:-2]
        return translate_type(base) + "[]"
    return _type_map.get(ifex_type, ifex_type)


# ---------------------------------------------------------------------------
# Node converters
# ---------------------------------------------------------------------------

def _convert_argument_in(arg: ifex.Argument) -> Parameter:
    return Parameter(
        name=arg.name,
        datatype=translate_type(arg.datatype),
        direction="in",
    )


def _convert_argument_out(arg: ifex.Argument) -> Parameter:
    return Parameter(
        name=arg.name,
        datatype=translate_type(arg.datatype),
        direction="out",
    )


def _convert_method(method: ifex.Method) -> Method:
    """Convert an IFEX Method to an AIDL Method.

    Return type: first element of method.returns if present, else void.
    Input arguments → in-parameters.
    Output arguments → out-parameters.
    """
    params: List[Parameter] = []

    for arg in (method.input or []):
        params.append(_convert_argument_in(arg))
    for arg in (method.output or []):
        params.append(_convert_argument_out(arg))

    # Determine return type
    returns = method.returns or []
    if returns:
        return_type = translate_type(returns[0].datatype)
    else:
        return_type = "void"

    return Method(
        name=method.name,
        return_type=return_type,
        parameters=params or None,
        oneway=False,
    )


def _convert_event(event: ifex.Event) -> Method:
    """IFEX Events become oneway void methods."""
    params = [_convert_argument_in(arg) for arg in (event.input or [])]
    return Method(
        name=event.name,
        return_type="void",
        parameters=params or None,
        oneway=True,
    )


def _convert_property(prop: ifex.Property) -> List[Method]:
    """IFEX Properties become a getter and (if not read-only) a setter."""
    aidl_type = translate_type(prop.datatype)
    getter = Method(
        name="get" + prop.name[0].upper() + prop.name[1:],
        return_type=aidl_type,
        parameters=None,
        oneway=False,
    )
    setter = Method(
        name="set" + prop.name[0].upper() + prop.name[1:],
        return_type="void",
        parameters=[Parameter(name="value", datatype=aidl_type, direction="in")],
        oneway=False,
    )
    return [getter, setter]


def _convert_interface(iface: ifex.Interface, package: str) -> AIDLFile:
    methods: List[Method] = []

    for m in (iface.methods or []):
        methods.append(_convert_method(m))
    for e in (iface.events or []):
        methods.append(_convert_event(e))
    for p in (iface.properties or []):
        methods.extend(_convert_property(p))

    aidl_iface = Interface(
        name="I" + iface.name,
        methods=methods or None,
    )
    return AIDLFile(package=package, declaration=aidl_iface)


def _convert_struct(struct: ifex.Struct, package: str) -> AIDLFile:
    fields = [
        ParcelableField(name=m.name, datatype=translate_type(m.datatype))
        for m in (struct.members or [])
    ]
    parcelable = Parcelable(name=struct.name, fields=fields or None)
    return AIDLFile(package=package, declaration=parcelable)


def _convert_enumeration(enum: ifex.Enumeration, package: str) -> AIDLFile:
    elements = [
        EnumElement(name=opt.name, value=str(opt.value) if opt.value is not None else None)
        for opt in (enum.options or [])
    ]
    aidl_enum = Enum(name=enum.name, elements=elements or None)
    return AIDLFile(package=package, declaration=aidl_enum)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def ifex_to_aidl(ast: ifex.AST) -> List[AIDLFile]:
    """Convert an IFEX AST into a list of AIDLFile objects (one per declaration).

    The IFEX Namespace name is used as the AIDL package name.
    Nested namespaces are flattened with dot-separated names.
    """
    files: List[AIDLFile] = []

    for ns in (ast.namespaces or []):
        _convert_namespace(ns, parent_package="", files=files)

    return files


def _convert_namespace(ns: ifex.Namespace, parent_package: str, files: List[AIDLFile]):
    package = (parent_package + "." + ns.name) if parent_package else ns.name

    # Interface
    if ns.interface is not None:
        files.append(_convert_interface(ns.interface, package))

    # Structs → Parcelables
    for struct in (ns.structs or []):
        files.append(_convert_struct(struct, package))

    # Enumerations → Enums
    for enum in (ns.enumerations or []):
        files.append(_convert_enumeration(enum, package))

    # Recurse into nested namespaces
    for child_ns in (ns.namespaces or []):
        _convert_namespace(child_ns, package, files)
