# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

from collections import OrderedDict
from dataclasses import fields, is_dataclass
from datetime import datetime, date
from transformers.rule_translator import  _log
from typing import get_args, get_origin, List, Optional, Union, Any, Dict, ForwardRef
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

#
# etc.

# As we traverse the tree of dataclass definitions, it can be quite difficult
# to keep track of which type each variable has.  Here is an explanation of how
# we try to keep track:
#
# The following functions come in two flavors each.  Functions like: is_xxx()
# take an object, which is an instance of typing.<some class> which is
# essentially an object that indicates the "type hint" using concepts from
# the 'typing' python module. Examples are: Optional, List, Union, Any, etc.
# In these functions we call variables that reference such a typing.Something
# object, a type_indicator.  The type_indicator corresponds to the type hint
# information on the right side of the colon : in an expression like this:
#
#    namespaces:  Optional[List[Namespace]]
#
# The type_indicator is the:  `Optional[List[Namespace]]`
# (or if fully qualified: `typing.Optional[typing.List[ifex_ast.Namespace]]`)
# The inner type can be an instance of an AST node, in other words an instance
# of a @dataclass like ifex_ast.Namespace, or it can be a built-in simple type
# like str.  e.g. typing.List[str]
#
# Next, in the 'dataclasses' python module we find the function: fields().
# fields() returns a list of the fields (i.e member variables) of the dataclass.
# Each field is represented by an object (an instance of the dataclasses.Field
# class).  In the following function we name variables that refer to such
# Field() instances as `field`.  A variable named field thus represents a
# member variable in the python (data)class.
#
# A field object contains several informations such as the name of the member
# variable (field.name), and the `.type` member, which gives us the
# type_indicator as described above.
#
# For each is_xxx() function, there is a convenience function named field_is_xxx()
# which takes an instance of the field itself, instead of the field's type.
# As you can see, most of those functions simply reference the field.type
# member to get the type_indicator, and then pass it the is_xxx() function.
#
# NOTE: Here in the descriptions we might refer to an object's "type" when we
# strictly mean its Type Indicator.  Since typing in python is dynamic,
# the actual type of an object could be different (and can be somewhat fungible
# too in theory, but usually not in this code).

# Note that is_dataclass() is true both for a class and a class instance (object)
# Hence, checking _also_ that t is type (class instance) is slightly stricter
def is_ast_class(t) -> bool:
    return isinstance(t, type) and is_dataclass(t)

# Rudimentary check - we assume what is passed is most likely part of the
# AST classes, and not some other @dataclass
def is_ast_type(t) -> bool:
    return is_dataclass(t)

# FIXME 2 functions are identical
def is_dataclass_type(cls):
    """Check if a class is a dataclass."""
    return is_dataclass(cls)

def is_optional(type_indicator):
    """Check if the type indicator is Optional."""
    # Note: Inside typing, Optional[MyType] is actually a Union of <MyType, None>.
    # So the following expression returns True if the type indicator is an Optional.
    return get_origin(type_indicator) is Union and type(None) in get_args(type_indicator)

def field_is_optional(field):
    """Check if the typing hint of a member field is Optional."""
    return is_optional(field.type)

def is_any(type_indicator):
    """Check if the type indicator is Any."""
    return type_indicator is Any

def field_is_any(field):
    """Check if the typing hint of a member field is Any."""
    return is_any(field.type)

def is_list(type_indicator):
    """Check if the type indicator is List (Optional or not)"""
    # If type indicator is wrapped in Optional we must extract the inner "actual type":
    if is_optional(type_indicator):
        return is_list(actual_type(type_indicator))
    else:
        return get_origin(type_indicator) is list

def field_is_list(field):
    """Check if the typing hint of a member field indicates that it is a List"""
    return is_list(field.type)

def inner_type(type_indicator):
    """Return the type of objects in the List *if* given a type indicator that is List.
    (Failure if type is not a List)"""
    if is_list(type_indicator):
        return get_args(actual_type(type_indicator))[0]

def field_inner_type(field):
    """Return the type of objects inside the List *if* given a *field* of type List.
    (Failure if type is not a List)"""
    return inner_type(field.type)

def actual_type(type_indicator):
    """Return the type X for a type indicator that is Optional[X].
    (Returns the type X also if input was non-optional)"""
    if type_indicator in [str, int]:
        return type_indicator
    if is_optional(type_indicator):
        return get_args(type_indicator)[0]
    else:
        return type_indicator

def field_actual_type(field):
    """Return the type X for a field that was defined as Optional[X]
    (Returns the type X also if input was non-optional)"""
    return actual_type(field.type)

def is_forwardref(type_indicator):
    """Check if type indicator is a ForwardRef"""
    return type(type_indicator) is ForwardRef

def field_is_forwardref(field):
    """Check if type indicator for a fieldo indicates that it is a ForwardRef"""
    return is_forwardref(field.type)

# This takes care about the fact that ForwardRef does not have a member
# __name__ (because it's not actually a type, as such). Instead it has
# __forward_arg__ which is a *string* containing the referenced type name.
def type_name(type_indicator):
    """Return the type name of the given type indicator, also supporting if it is a ForwardRef"""
    if is_forwardref(type_indicator):
        return type_indicator.__forward_arg__
    else:
        return type_indicator.__name__

def field_referenced_type(f):
    """Return the type of the field, but if it's a list, return the type inside the list"""
    if field_is_list(f):
        return field_inner_type(f)
    else:
        return field_actual_type(f)

def is_simple_type(t) -> bool:
    return t in [str, int, float, bool, date, datetime]

def is_empty(node) -> bool:
    if type(node) is str:
        return node == ""
    elif type(node) is list:
        return node == []
    else:
        return node is None

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

VERBOSE = False

# Tree processing function:
def walk_type_tree(node, process, seen={}):
    """Walk the AST class hierarchy as defined by @dataclasses with type
    hints from typing module.

    Performs a depth-first traversal.  Parent node is processed first, then its
    children, going as deep as possible before backtracking. Type names that have
    already been seen before are identical so recursion is cut off there.
    The given hook function "process" is called for every unique type.

    Arguments: node = a @dataclass class
               process = a "callback" function to call for each node"""

    # (No need to document, or recurse on the following types):
    # FIXME: this is correct for our documentation generation but maybe not for all cases
    # or we may change condition to:  "if not is_dataclass"
    if node in [str, int, Any, bool]:
        return

    # Skip duplicates (like Namespace, it appears more than once in the AST model)
    name = type_name(node)
    if seen.get(name):
        if VERBOSE:
            _log("INFO", f"   note: a field of type {name} was skipped")
        return

    seen[name] = True

    # Process this node
    process(node)

    # ForwardRef will fail if we try to recurse over its children.
    # However, the types that are handled with ForwardRef (Namespace)
    # ought to appear anyhow somewhere else in the recursion, so we
    # skip them.
    if is_forwardref(node):
        return

    # Next, recurse on each AST type used in child fields (stripping
    # away 'List' and 'Optional' to get to the interesting class)
    for f in fields(node):
        if field_is_list(f):
            if VERBOSE:
                print(f"   field: {f.name}")
            # Document Node types that are found inside Lists
            walk_type_tree(field_inner_type(f), process, seen)
        else:
            # Document Node types found directly
            walk_type_tree(field_actual_type(f), process, seen)



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
    from models.common.type_checking_constructor_mixin import add_constructors_to_ast_model
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
