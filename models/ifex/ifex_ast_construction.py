# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

"""
Light-weight support functions for creating an IFEX tree from program code,
likely to be used in X-to-IFEX model conversions.
"""

# This module supports creating of an IFEX internal tree from python code.  It
# is likely to be used in a <something>-to-IFEX (model-to-model) conversion.
# It also adds a printout function so that an internal IFEX tree "AST"
# representation can be printed out in the IFEX Core IDL format (in YAML)

# Many programs that need to create IFEX are better off using a input-to-model
# or model-to-model transformation (build the IFEX tree internally, and *then*
# print text), compared to immediately printing IFEX core IDL text (YAML).

# This code gives primitive but useful support.  It is simply implemented by
# adding constructor (__init__) functions for the @dataclass node definitions
# in ifex_ast.py. Object creation was of course already possible because
# @dataclasses have automatic __init__ functions.  However, using the
# type_checking_constructor_mixin code, it performs some type-checking of
# the given inputs, which helps to avoid simply printing out a non-compliant
# YAML document.

# With __init__ it is possible to create an object tree in a straight forward
# and expected way, including some type checks:
#
#    from models.ifex import ifex_ast_construction 
#    from models.ifex.ifex_ast import Namespace, Interface, ...
#
#    # Initialize support:
#    ifex_ast_construction.add_constructors_to_ifex_ast_model()
#
#    # Create objects and link them together.
#    ns = Namespace('mynamespacename', description = 'this is it')
#    if = Interface('the-interface-node')
#    ns.interface = if
#
#    # (Re)assign member fields on any object
#    ns.interface.methods = [... method objects...]
#
# etc.

from collections import OrderedDict
from dataclasses import is_dataclass, fields
from datetime import date, datetime
from models.ifex import ifex_ast
from models.ifex.type_checking_constructor_mixin import add_constructor

# Use the oyaml library because it supports OrderedDict. We can output keys in
# the order they are defined in the AST classes (e.g. "name" comes first!)
import oyaml

def add_constructors_to_ifex_ast_model() -> None:
    """ Mix in the type-checking constructor support into each of the ifex_ast classes: """
    for c in [cls for cls in ifex_ast.__dict__.values() if
              isinstance(cls, type) and
              is_dataclass(cls)]:
        add_constructor(c)


def is_empty(node) -> bool:
    if type(node) is str:
        return node == ""
    elif type(node) is list:
        return node == []
    else:
        return node is None

def is_simple_type(t) -> bool:
    return t in [str, int, float, bool, date, datetime]

def ifex_ast_to_dict(node, debug_context="") -> OrderedDict:

    """Given a root node, return a key-value mapping dict (which represents the YAML equivalent). The function is recursive. """

    if node is None:
        raise TypeError(f"None-value should not be passed to function, parent debug: {debug_context=}")

    # Strings and Ints are directly understood by the YAML output printer so just put them in.
    if is_simple_type(type(node)):
        return node

    # In addition to dicts, we might have python lists, which will be output as lists in YAML
    #if is_list(node) or type(node) == list:
    if type(node) is list:
        ret = []
        for listitem in node:
            ret.append(ifex_ast_to_dict(listitem, debug_context=str(node)))
        return ret

    # New dict containing all key-value pairs at this level
    ret = OrderedDict()

    # Recursively process all fields in this object type.
    # Empty fields should not be unnecessarily listed in the resulting YAML, so
    # we skip them.  Note that empty items can happen only on fields that are
    # Optional, otherwise the type-checking constructor would have caught the
    # error.

    for f in fields(node):
        item = getattr(node, f.name)
        if not is_empty(item):
            ret[f.name] = ifex_ast_to_dict(item, debug_context=str(f))

    return ret


def ifex_ast_as_yaml(node):
    return oyaml.dump(ifex_ast_to_dict(node))

# ----------------- TEST CODE BELOW --------------------

if __name__ == '__main__':
    from models.ifex.ifex_ast import AST, Namespace, Interface, Method, Argument

    # How to create a AST representation in code:
    root = AST('test')
    ns1 = Namespace('name_ns1')
    root.namespaces = [ns1, Namespace('another_empty_namespace')]
    if_a = Interface('name_if_a')
    if_a.methods.append(Method('mymethod'))
    m = Method('mymethod2', description = "This is the second method", input = [Argument(name='val', datatype='uint32')])
    if_a.methods.append(m)
    ns1.interface = if_a

    print("\n--- Test objects converted to dict: ---")
    print(ifex_ast_to_dict(root))
    print("\n--- Test objects as YAML: ---")
    print(ifex_ast_as_yaml(root))
