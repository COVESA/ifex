# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

from collections import OrderedDict
from dataclasses import fields
from datetime import datetime, date
from models.ifex.ifex_ast_introspect import is_optional
from transformers.rule_translator import  _log
from typing import Any, Dict 
import models.common.type_checking_constructor_mixin
import oyaml

# This module supports creating and processing an IFEX internal tree, and many
# similar models for other IDLs, from python code.  
# a <something>-to-IFEX (model-to-model) conversion.  
# It also adds a printout function so that an internal IFEX tree "AST"
# representation can be printed out in the IFEX Core IDL format (in YAML)

# Many programs that need to transform to/from IFEX are better off using a input-to-model
# or model-to-model transformation (build the new AST internally, and *then*
# print text), as compared to immediately printing IFEX core
# IDL, or another IDL format as text.

# This code gives primitive but useful support.  It is simply implemented by
# adding constructor (__init__) functions for the @dataclass node definitions
# in ifex_ast.py. Object creation was of course already possible because
# @dataclasses have automatic __init__ functions.  However, using the
# type_checking_constructor_mixin code, it performs some type-checking of
# the given inputs, which helps to avoid creating a non-compliant AST model

# With __init__ it is possible to create an object tree in a straight forward
# and expected way, including some type checks:
#
#    from models.ifex.ifex_ast import Namespace, Interface, ...
#    import models.common.ast_utils
#
#    # Initialize support:
#    ast_utils.add_constructors_to_ast_model()
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


def add_constructors_to_ast_model(module) -> None:
    """ Mix in the type-checking constructor support into each of the ifex_ast classes: """
    for c in [cls for cls in module.__dict__.values() if
              isinstance(cls, type) and
              is_dataclass(cls)]:
        type_checking_constructor_mixin.add_constructor(c)

def is_empty(node) -> bool:
    if type(node) is str:
        return node == ""
    elif type(node) is list:
        return node == []
    else:
        return node is None

# Note that is_dataclass() is true both for a class and a class instance (object)
# Hence, checking _also_ that t is type (class instance) is slightly stricter
def is_ast_class(t) -> bool:
    return isinstance(t, type) and is_dataclass(t)

# Rudimentary check - we assume what is passed is most likely part of the
# AST classes, and not some other @dataclass
def is_ast_type(t) -> bool:
    return is_dataclass(t)

def is_simple_type(t) -> bool:
    return t in [str, int, float, bool, date, datetime]

# Factoring out some of the boolean checks:

def type_match(node, type_) -> bool:
    # Pass Any as type == wildcard matches everything...otherwise compare types
    return type_ == Any or (type(node) ==  type_)

def name_match(node, name) -> bool:
    # Note that "*" is considered wildcard - matches any name!
    return hasattr(node, 'name') and (getattr(node, 'name') == name or name == "*")

def type_and_name_match(node, name, type_) -> bool:
    return type_match(node, type_) and name_match(node, name)

def field_match(node, field_name, value) -> bool:
    # Note that "*" is considered wildcard - matches any value!
    return hasattr(node, field_name) and (getattr(node, field_name) == value or value == "*")

def all_fields_match(node, field_values: Dict[str, Any]) -> bool:
    return all(field_match(node, field_name, value) for field_name, value in field_values.items())

# There could be more optimized versions of these convenience functions, but to
# keep complexity down, DRY code, and avoiding bugs, let's delegate to the most
# generic function and get that one right.  Later, optimizations could be made.

def find_first_by_name(node, name: str, recursive: bool = True) -> Any:
    return find_first_impl(node, lambda node: name_match(node, name), recursive)

def find_all_by_name(node, name: str, recursive: bool = True) -> list:
    return find_all_impl(node, lambda node: name_match(node, name), recursive)

def find_first_by_type(node, type_: str, recursive: bool = True) -> Any:
    return find_first_impl(node, lambda node: type_match(node, type_), recursive)

def find_all_by_type(node, type_: str, recursive: bool = True) -> list:
    return find_all_impl(node, lambda node: type_match(node, type_), recursive)

def find_first_by_name_and_type(node, name, type_, recursive: bool = True) -> Any:
    return find_first_impl(node, lambda node: type_and_name_match(node, name, type_), recursive)

def find_all_by_name_and_type(node, name, type_, recursive: bool  = True) -> list:
    return find_all_impl(node, lambda node: type_and_name_match(node, name, type_), recursive)

def find_first_by_fields(node, field_values: Dict[str, Any], recursive: bool  = True) -> Any:
   return find_first_impl(node, lambda node: all_fields_match(node, field_values), recursive)

def find_all_by_fields(node, field_values: Dict[str, Any], recursive: bool = True) -> list:
    return find_all_impl(node, lambda node: all_fields_match(node, field_values), recursive)

def find_first_impl(node, match_function: callable, recursive: bool = True) -> Any:
    # Very silly implementation for now -> find all, and then return the first one
    # TODO (later): Implement new function so it terminates on the first match
   found = find_all_impl(node, match_function, recursive)
   if found is not None:
       if isinstance(found, list):
           if found != []:
               return found[0]
           else:
               return None
       else:
           return found
   return None

# Main implementation.  Iterates over the tree and applies the given
# match_function on each node to see if this is considerd to match the
# conditions.  Return a list of all matching items.  If recursive is False,
# it only searches the first level of items!
def find_all_impl(node: Any, match_function: callable, recursive: bool = True) -> list:

    results = []
    # Recurse over lists, and combine results
    if isinstance(node, list):
        # Run on each one, then flatten result
        matches = [find_all_impl(item, match_function, recursive) for item in node]
        return [x for list_ in matches for x in list_]

    # Found match?
    if match_function(node):
        results.append(node)
    else:
        _log("DEBUG", f"## {node=} is not matching {match_function=}")
        pass

    # TODO - flip logic around here, check for list first, check if
    # is_ast_type() and only then run fields(). Then do recursive check
    if recursive:
        _log("DEBUG", f"Recursive find: Iterate over fields in {node=}")
        for field in fields(node):
            value = getattr(node, field.name)
            if isinstance(value, list):
                for item in value:
                    results.extend(find_all_impl(item, match_function, recursive))
            elif is_ast_type(value):
                results.extend(find_all_impl(value, match_function, recursive))
    else:
        for field in fields(node):
            value = getattr(node, field.name)
            if match_function(value):
                results.append(value)

    return results


# Prune: Search through tree for matching nodes, and "delete" them (by setting
# the field equal to None). If force is false, it will create an error if an
# invalid model would result because a mandatory variable is unset.  If force
# is true, an invalid model is possible.
# FIXME: Does not look at recursive flag
def prune(node: Any, field_values: Dict[str, Any], recursive=True, force=False):

    if is_ast_type(node):
        for field in fields(node):
            value = getattr(node, field.name)
            if isinstance(value, list):
                # Looping using indexes? Yes, because we need a *reference* to
                # the actual item in the list so it can be modified.  Using
                # "for val in field_values" would create a copy, not the real reference.
                for i in range(len(value)):
                    prune(value[i], field_values)

            # Prune single item if matching
            elif all_fields_match(node, field_values):
                if is_optional(field) or force:
                    setattr(node, field, None)
                else:
                    raise Exception("Prune tried to delete node which is mandatory. Use force=true to override")

            # Recurse over objects to reach the rest of the tree
            elif is_ast_type(value):
                prune(value, field_values)

# Convert any AST (if represented by our standard set of @dataclass nodes) to a
# dict representation, which can then be printed out as YAML if desired.
# (see oyaml....)
# The resulting YAML is the actual YAML representation of the IFEX model.  
# For other models, YAML may not be the natural representation, but can be
# useful for studying/debugging

def ast_to_dict(node, debug_context="") -> OrderedDict:

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
            ret.append(ast_to_dict(listitem, debug_context=str(node)))
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
            ret[f.name] = ast_to_dict(item, debug_context=str(f))

    return ret

def dict_as_yaml(d):
    return oyaml.dump(d)

def ast_as_yaml(node):
    return dict_as_yaml(ast_to_dict(node))

# --- Script entry point ---
if __name__ == '__main__':

    # The tree functions should be generic but this test code is based on protobuf
    import os
    import sys
    import models.protobuf.protobuf_ast as protobuf
    from protobuf_to_ifex import proto_to_ifex
    from models.protobuf.protobuf_lark import get_ast_from_proto_file

    if len(sys.argv) != 2:
        print(f"Usage: python {os.path.basename(__file__)} <filename>")
        sys.exit(1)

    # Add the type-checking constructor mixin
    add_constructors_to_ast_model(protobuf)

    try:
        # Parse protobuf input and create Protobuf AST
        proto_ast = get_ast_from_proto_file(sys.argv[1])
        print(proto_ast)

        # Output as YAML
        print(ast_as_yaml(proto_ast))

        print(f"{find_first_by_name(proto_ast, 'S_UNSPECIFIED')=}")
        print(f"{find_first_by_fields(proto_ast, { 'value' : '4'  })=}")
        print(f"{find_first_by_fields(proto_ast, { 'datatype' : 'int32'  })=}")
        print(f"{find_all_by_fields(proto_ast, { 'datatype' : 'int32'  }, recursive=False)=}")
        print(f"{proto_ast.messages[0].fields=}")
        print(f"{find_all_by_fields(proto_ast.messages[0].fields, { 'datatype' : 'int32'  })=}")
        print(f"{find_all_by_fields(proto_ast.messages, { 'datatype' : 'int32'  })=}")
        print(f"{find_first_by_fields(proto_ast.messages, { 'datatype' : 'int32'  })=}")
        print(f"{find_first_by_name_and_type(proto_ast, 'innerinner', protobuf.Field)=}")
        print(f"{find_first_by_name(proto_ast, 'innerinner')=}")
        print(f"{find_first_by_name_and_type(proto_ast, 'innerinner', protobuf.Field)=}")
        print(f"{find_all_by_name(proto_ast, 'innerinner', protobuf.Field)=}")

    except FileNotFoundError:
        _log("ERROR", "File not found")

    except Exception as e:
        _log("ERROR", f"An unexpected error occurred: {e}")
        raise(e)
