# SPDX-License-Identifier: MPL-2.0
# ----------------------------------------------------------------------------
# (C) 2023 Novaspring AB
# Type resolver for the D-Bus XML format generator
# ----------------------------------------------------------------------------

from models.ifex.ifex_ast import (
    AST,
    Namespace,
    Interface,
    Enumeration,
    Member,
    Struct,
    Typedef,
)
from models.ifex import ifex_parser
import sys

# D-Bus basic types, as defined in [D-Bus Specification](https://dbus.freedesktop.org/doc/dbus-specification.html#basic-types)
#
# Conventional name|ASCII type-code|Encoding
# -----------------|---------------|---------
# BYTE              y (121)         Unsigned 8-bit integer
# BOOLEAN           b (98)          Boolean value: 0 is false, 1 is true
# INT16             n (110)         Signed (two's complement) 16-bit integer
# UINT16            q (113)         Unsigned 16-bit integer
# INT32             i (105)         Signed (two's complement) 32-bit integer
# UINT32            u (117)         Unsigned 32-bit integer
# INT64             x (120)         Signed (two's complement) 64-bit integer
# UINT64            t (116)         Unsigned 64-bit integer
# DOUBLE            d (100)         IEEE 754 double-precision floating point
# UNIX_FD           h (104)         32-bit index into array of file descriptors

# And later in spec another table that adds more types:

# OBJECT_PATH 111 'o' Name of an object instance
# SIGNATURE   103 'g' A type signature
# ARRAY   97 'a'  Array
# STRUCT  114 'r', 40 '(', ')'
#                type code 114 'r' is reserved for use in bindings and
#                implementations to represent the general concept of a struct,
#                and must not appear in signatures used on D-Bus.
# VARIANT 118 'v'     Variant type (the type of the value is part of the value itself)
# DICT_ENTRY  'e', '{', '}'   Entry in a dict or map (array of key-value pairs). Type code 101 'e' is reserved for use in bindings and implementations to represent the general concept of a dict or dict-entry, and must not appear in signatures used on D-Bus.

ifex_to_dbus_types = {
    "uint8": "y",
    "int8": "y",   # Coerce int8 into uint8 for D-Bus support
    "uint16": "q",
    "int16": "n",
    "uint32": "u",
    "int32": "i",
    "uint64": "t",
    "int64": "x",
    "float": "d",  # Promote float to double for D-Bus support
    "double": "d",
    "string": "s",
    "boolean": "b",
    # TODO: map/dict, set, variant
}
# PRELIMINARY:
# v is for an unknown type (variant type, supported by D-Bus standard)
# X is to indicate that we shall replace X by a concrete type definition
ifex_complex_types_to_dbus = {
    "set": "aX",     # Sets transferred as D-Bus arrays
    "map": "a{Xv}",  # In IFEX keys of a dict/map can be any type
    "opaque": "v",   # Opaque is an unknown/undefined type
}

# Helper functions:

# which is very simply that the string name includes: '[]'
def is_array(typename):
    """Answers if it's an array type. Primitive/known types only - does not
    resolve deep references."""
    return isinstance(typename, str) and typename.find("[") != -1


# If it is an array (as defined in previous comment), return the member type of
# the array (which means simply strip off the '[]') e.g. uint32[10] -> uint32
def get_array_member(typename):
    return typename.split("[")[0]


# Main IFEX to D-Bus type translator:  This function will recurse until a D-Bus
# supported primitive type has been created.
def gen_dbus_type(ifextype):
    dbus_type = ""
    # Iterate over lists
    if isinstance(ifextype, list):
        for t in ifextype:
            dbus_type += f"{t} => {gen_dbus_type(t)}\n"
    # Array of items
    elif is_array(ifextype):
        dbus_type += "a" + gen_dbus_type(get_array_member(ifextype))
    # Typedef/Enumeration -> just translate to the underlying type
    elif isinstance(ifextype, Typedef) or isinstance(ifextype, Enumeration):
        dbus_type += gen_dbus_type(ifextype.datatype)
    # Struct of items -> parentheses, and recurse on struct members
    elif isinstance(ifextype, Struct):
        dbus_type += "("
        for m in ifextype.members:
            dbus_type += gen_dbus_type(m)
        dbus_type += ")"
    # Member (of Struct) -> translate its datatype
    elif isinstance(ifextype, Member):
        dbus_type += gen_dbus_type(ifextype.datatype)
    # Direct type name, (non-array)
    else:
        dbt = ifex_to_dbus_types.get(ifextype)
        known_type = known_ifex_type_definitions.get(ifextype)
        if dbt is not None:
            dbus_type += dbt
        elif known_type is not None:
            dbus_type += gen_dbus_type(known_type)
        else:
            dbus_type += f"UNKNOWN_TYPE({ifextype})"

    return dbus_type


# Registry for type definitions taken from the IFEX file
# (or included files):
known_ifex_type_definitions = {}

# Complex types (typedefs, structs, enums...) can refer to other complex
# types, not only to primitive types.
# In this function we do a first iteration to register all defined types.
# so that their definition is known when they are referenced later.

# collect_types() shall be called with all IFEX files that contain types that we
# need to convert. (i.e. any type that _could_ be referenced by another type in the
# converted interface file)


# NOTE! This collects into a module-global variable `known_ifex_type_definitions`
# => no multithreading/parallel use.
# (if later needed the module shall be converted into an instantiable class instead)
# The node parameter is a dataclass instance, as returned from the dacite conversion
def collect_types(node):
    # FIXME: Shall this also handle partial type-defining files that lack namespace structure?

    # Recurse over each instance in a list
    if type(node) is list:
        for listitem in node:
            collect_types(listitem)
        return

    # Recurse on each (sub)-namespace
    if type(node) in [Namespace, AST]:
        collect_types(node.namespaces)

    # Types can be collected from either a Namespace or an Interface
    if type(node) in [Interface, Namespace]:
        for x in node.structs:
            known_ifex_type_definitions[x.name] = x
        for x in node.typedefs:
            known_ifex_type_definitions[x.name] = x.datatype
        for x in node.enumerations:
            known_ifex_type_definitions[x.name] = x.datatype

    # Finally, a single Interface can be underneath any Namespace
    if type(node) is Namespace and node.interface is not None:
        collect_types(node.interface)


# main() = FOR MODULE TEST ONLY - NOT USED BY MAIN CODE GENERATOR
def main():
    file = sys.argv[1]

    tree = ifex_parser.get_ast_from_yaml_file(file)
    collect_types(tree.namespaces)

    print("TEST EXECUTABLE FOR D-BUS TYPE DEFINITIONS")
    for n in tree.namespaces:
        if n.interface is not None:
            i=n.interface
            interface_items = i.structs + i.typedefs + i.enumerations
        else:
            interface_items = []
        for x in n.structs + n.typedefs + n.enumerations + interface_items:
            print(
                "--------------------------------------------------------------------"
            )
            print(f"Translating IFEX type: {x}")
            transl = gen_dbus_type(x)
            print("D-Bus equivalent: ", end="")
            print(transl)


if __name__ == "__main__":
    main()
