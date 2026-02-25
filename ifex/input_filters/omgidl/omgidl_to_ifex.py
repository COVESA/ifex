# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project
# vim: tw=120 ts=4 et

"""
Convert an OMG IDL AST (IDLFile) to an IFEX AST (ifex.AST).

Public API:
    omgidl_to_ifex(idl_file: IDLFile) -> ifex.AST

Follows the same approach as aidl_to_ifex.py / protobuf_to_ifex.py:
  - Manual tree-walking (no rule_translator)
  - Capitalised function names to make AST type names stand out

Mapping summary
---------------
OMG IDL                          IFEX
-------                          ----
Module                       ->  Namespace (nested modules = nested Namespaces)
Interface                    ->  ifex.Interface (inside a Namespace)
Operation(oneway=False)      ->  ifex.Method
Operation(oneway=True)       ->  ifex.Event
Parameter(dir="in"/"inout")  ->  Argument in Method.input
Parameter(dir="out"/"inout") ->  Argument in Method.output
return_type != "void"        ->  Argument(name="_return") in Method.returns
raises clause                ->  Method.errors (list of ifex.Error)
Attribute                    ->  ifex.Property
Attribute(readonly=True)     ->  ifex.Property (description notes read-only)
Struct                       ->  ifex.Struct
Member                       ->  ifex.Member
Enum                         ->  ifex.Enumeration (datatype="int32", values 0,1,2,...)
Enumerator                   ->  ifex.Option
Exception_                   ->  ifex.Struct (name prefixed "Ex_")
Typedef                      ->  ifex.Typedef

Top-level declarations (outside any module) are collected into a single
anonymous Namespace named "_global_".

For a file with a single top-level module, the result is:
    ifex.AST(namespaces=[Namespace(name=module.name, ...)])
"""

import ifex.models.ifex.ifex_ast as ifex
from ifex.models.omgidl.omgidl_ast import (
    IDLFile, Module, Interface, Operation, Attribute, Const,
    Parameter, Struct, Enum, Enumerator, Exception_, Typedef, Member,
)


# ============================================================
# Type translation  (OMG IDL primitives → IFEX types)
# ============================================================

_type_map = {
    # Exact OMG IDL primitive type names → IFEX fundamental types
    "boolean":            "boolean",
    "octet":              "uint8",
    "char":               "uint8",
    "wchar":              "uint8",
    "short":              "int16",
    "unsigned short":     "uint16",
    "long":               "int32",
    "unsigned long":      "uint32",
    "long long":          "int64",
    "unsigned long long": "uint64",
    "float":              "float",
    "double":             "double",
    "long double":        "double",   # IFEX has no extended precision
    "string":             "string",
    "wstring":            "string",
    "any":                "opaque",
    "Object":             "opaque",
    "void":               "void",     # internal sentinel
}


def translate_type(t: str) -> str:
    """Map an OMG IDL type string to an IFEX type string.

    Handles:
    - Primitive types via _type_map
    - Array types: "long[3]" → "int32[]"  (size information is lost)
    - Sequence types: "sequence<float>" → "float[]"
                      "sequence<float,10>" → "float[]"  (bound lost)
    - Unknown / user-defined types pass through unchanged.
    """
    # sequence<T> or sequence<T,N>
    if t.startswith("sequence<"):
        inner = t[len("sequence<"):].rstrip(">")
        # strip optional bound ",N"
        elem_type = inner.split(",")[0].strip()
        return translate_type(elem_type) + "[]"

    # Fixed-size array: "long[3]" — strip the [N] suffix
    if "[" in t:
        base = t[:t.index("[")].strip()
        return translate_type(base) + "[]"

    return _type_map.get(t, t)


# ============================================================
# Conversion helpers  (Capitalised names = AST types visible)
# ============================================================

def Params_to_Input(parameters) -> list:
    return [ifex.Argument(name=p.name, datatype=translate_type(p.datatype))
            for p in (parameters or []) if p.direction in ('in', 'inout')]


def Params_to_Output(parameters) -> list:
    return [ifex.Argument(name=p.name, datatype=translate_type(p.datatype))
            for p in (parameters or []) if p.direction in ('out', 'inout')]


def Operation_to_Returns(op: Operation) -> list:
    if op.return_type and op.return_type != 'void':
        return [ifex.Argument(name='_return', datatype=translate_type(op.return_type))]
    return []


def Raises_to_Errors(raises) -> list:
    """Convert a raises list (exception type names) to ifex.Error objects."""
    return [ifex.Error(datatype=name) for name in (raises or [])]


def Operations_to_Methods(operations) -> list:
    result = []
    for op in (operations or []):
        if op.oneway:
            continue
        input_args  = Params_to_Input(op.parameters)
        output_args = Params_to_Output(op.parameters)
        returns     = Operation_to_Returns(op)
        errors      = Raises_to_Errors(op.raises)
        result.append(ifex.Method(
            name    = op.name,
            input   = input_args  if input_args  else None,
            output  = output_args if output_args else None,
            returns = returns     if returns     else None,
            errors  = errors      if errors      else None,
        ))
    return result


def Operations_to_Events(operations) -> list:
    result = []
    for op in (operations or []):
        if not op.oneway:
            continue
        input_args = Params_to_Input(op.parameters)
        result.append(ifex.Event(
            name  = op.name,
            input = input_args if input_args else None,
        ))
    return result


def Attribute_to_Property(attr: Attribute) -> ifex.Property:
    desc = "readonly" if attr.readonly else None
    return ifex.Property(name=attr.name, datatype=translate_type(attr.datatype),
                         description=desc)


def Members_to_Members(members) -> list:
    return [ifex.Member(name=m.name, datatype=translate_type(m.datatype))
            for m in (members or [])]


def Struct_to_Struct(s: Struct) -> ifex.Struct:
    return ifex.Struct(
        name    = s.name,
        members = Members_to_Members(s.members) or None,
    )


def Exception_to_Struct(e: Exception_) -> ifex.Struct:
    """Convert an IDL exception to an IFEX Struct, prefixing name with Ex_."""
    return ifex.Struct(
        name    = "Ex_" + e.name,
        members = Members_to_Members(e.members) or None,
    )


def Enum_to_Enumeration(e: Enum) -> ifex.Enumeration:
    """Convert an IDL enum to an IFEX Enumeration.

    OMG IDL enumerators have no explicit integer values; they are
    assigned 0, 1, 2, ... in declaration order.
    """
    options = []
    for idx, en in enumerate(e.enumerators or []):
        options.append(ifex.Option(name=en.name, value=idx))
    return ifex.Enumeration(
        name     = e.name,
        datatype = 'int32',
        options  = options,
    )


def Typedef_to_Typedef(t: Typedef) -> ifex.Typedef:
    return ifex.Typedef(name=t.name, datatype=translate_type(t.datatype))


def Interface_to_Interface(iface: Interface) -> ifex.Interface:
    methods    = Operations_to_Methods(iface.operations)
    events     = Operations_to_Events(iface.operations)
    properties = [Attribute_to_Property(a) for a in (iface.attributes or [])]
    return ifex.Interface(
        name       = iface.name,
        methods    = methods    if methods    else None,
        events     = events     if events     else None,
        properties = properties if properties else None,
    )


def Module_to_Namespace(module: Module) -> ifex.Namespace:
    """Recursively convert a Module to a Namespace."""
    structs      = [Struct_to_Struct(s)      for s in (module.structs     or [])]
    structs     += [Exception_to_Struct(e)   for e in (module.exceptions  or [])]
    enumerations = [Enum_to_Enumeration(e)   for e in (module.enums       or [])]
    typedefs     = [Typedef_to_Typedef(t)    for t in (module.typedefs    or [])]
    sub_ns       = [Module_to_Namespace(m)   for m in (module.modules     or [])]

    ns = ifex.Namespace(
        name         = module.name,
        structs      = structs      if structs      else None,
        enumerations = enumerations if enumerations else None,
        typedefs     = typedefs     if typedefs     else None,
        namespaces   = sub_ns       if sub_ns       else None,
    )

    # At most one interface per namespace in IFEX
    if module.interfaces:
        if len(module.interfaces) > 1:
            # Multiple interfaces: take the first and warn
            import sys
            print(f"WARNING: module '{module.name}' has {len(module.interfaces)} interfaces; "
                  f"only '{module.interfaces[0].name}' is mapped to ifex.Interface. "
                  f"Remaining interfaces are ignored.", file=sys.stderr)
        ns.interface = Interface_to_Interface(module.interfaces[0])

    return ns


# ============================================================
# Main conversion entry point
# ============================================================

def omgidl_to_ifex(idl_file: IDLFile) -> ifex.AST:
    """Convert an IDLFile AST to an IFEX AST.

    Each top-level module becomes a Namespace.  Top-level declarations
    outside any module are placed in a single '_global_' Namespace.

    :param idl_file: parsed IDLFile AST
    :return: ifex.AST
    """
    namespaces = []

    # Modules → Namespaces
    for module in (idl_file.modules or []):
        namespaces.append(Module_to_Namespace(module))

    # Top-level declarations outside any module → '_global_' Namespace
    global_structs      = [Struct_to_Struct(s)    for s in (idl_file.structs     or [])]
    global_structs     += [Exception_to_Struct(e) for e in (idl_file.exceptions  or [])]
    global_enums        = [Enum_to_Enumeration(e) for e in (idl_file.enums       or [])]
    global_typedefs     = [Typedef_to_Typedef(t)  for t in (idl_file.typedefs    or [])]

    global_ns = None
    if global_structs or global_enums or global_typedefs or idl_file.interfaces:
        global_ns = ifex.Namespace(
            name         = '_global_',
            structs      = global_structs  if global_structs  else None,
            enumerations = global_enums    if global_enums    else None,
            typedefs     = global_typedefs if global_typedefs else None,
        )
        if idl_file.interfaces:
            global_ns.interface = Interface_to_Interface(idl_file.interfaces[0])
        namespaces.append(global_ns)

    return ifex.AST(namespaces=namespaces if namespaces else None)
