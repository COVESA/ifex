# SPDX-License-Identifier: MPL-2.0

# (C) 2023 MBition GmbH
# (C) 2022 Novaspring AB
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Provide helper functions to inspect the IFEX Core IDL language definition,
as it is defined by the AST structure tree/hierarchy (not an inheritance hierarchy)
in the `ifex_ast` python file.  These function can be used by implementations
that process the IFEX AST, or any other model designed in the same way.
"""

import re
import models.ifex.ifex_ast as ifex_ast
from dataclasses import is_dataclass, fields
from typing import get_args, get_origin, List, Optional, Union, Any, ForwardRef
import typing

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


# --- End of generic functions --

# ------------------------------------------------------------------------------------------------
# Above thes line we had generic functions that give information about a AST-model built
# from a number of @dataclasses and field typing information.
#
# We can notice that those only refers to *python* concepts such as @dataclasses and the typing module.
# This means, those functions could also be used for other similarly described AST models, beyond
# the IFEX Core IDL model.
#
# Below this line follows functions that are specific to IFEX. For example is_ifex_variant_typedef evaluates
# an actual IFEX-specific concern about the IFEX variant type.  It is not a variant type of the python
# typing concept (which is called typing.Union anyhow) - these functions are about IFEX-specific concerns.

# Check if string is "variant<something>" where something can be empty
p_shortform_variant0 = r'variant<\s*([^,]*\s*(?:,\s*[^,]*)*)\s*>'

# ...and this for variant<at_least_one>
p_shortform_variant1 = r'variant<\s*([^,]+(?:\s*,\s*[^,]+)*)\s*>'

# ...and this is the one we actually need. A valid variant has at least 2
# types listed or it would not make sense. This last pattern guarantees this:
p_shortform_variant2 = r'variant<\s*[^,]+(?:\s*,\s*[^,]+)+\s*>'

def is_ifex_variant_shortform(s):
    """ Answer if a Typedef object has datatype defined to using the short form: variant<type1,type2,type3...> """

    # Convert "truthy" result object to actual bool for nicer debugging
    return bool(s and s != '' and re.match(p_shortform_variant2, s))

def is_ifex_variant_typedef(f):
    """ Answer if a Typedef object uses a variant type.
    A variant type can be defined in either one of these two ways:
    1. The field "datatypes" has a value, in other words there is a *list* of datatypes, as opposed to only one
    or:
    2. That the short form syntax is used in the datatype name:  variant<type1,type2,...>."""

    # Convert "truthy" result object to actual bool for nicer debugging
    return bool( isinstance(f, ifex_ast.Typedef) and (f.datatypes or is_ifex_variant_shortform(f.datatype)) )

def is_ifex_invalid_typedef(f):
    """Check if both a single and multiple datatypes are defined. That is invalid."""
    return is_ifex_variant_typedef(f) and f.datatype and f.datatypes

def get_variant_types(obj):
    """Return a list of the types handled by the given variant type.  The function accepts either a Typedef object or a string with the type name. The string must then be the variant<a,b,c> fundamental type - it cannot be the name of a typedef."""
    if isinstance(obj, ifex_ast.Typedef):
        if is_ifex_invalid_typedef(obj):
            raise TypeException('Provided variant object is misconfigured')
        # Process datatypes list
        if obj.datatypes:
            return obj.datatypes
        # or process single datatype (string)
        else: 
            return get_variant_types(obj.datatype)
    elif type(obj) == str:
        match = re.search(r'variant *<(.*?)>', obj)
        if match:
            types = match.group(1).split(',')
            return [t.strip() for t in types]

    # (else) Any other cases = error
    raise Exception('Provided object is not a variant type: {obj=}')

# ------------------------------------------------------------------------------------------------

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
    if node in [str, int, typing.Any]:
        return

    # Skip duplicates (like Namespace, it appears more than once in the AST model)
    name = type_name(node)
    if seen.get(name):
        if VERBOSE:
            print(f"   note: a field of type {name} was skipped")
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


# Test code:

# Comment: Here's one way to get the typing hints of a member of a
# dataclass from typing import: get_type_hints
# print(get_type_hints(ifex_ast.Namespace)['interface'])

# Simple processor function for testing - just print the text representation of the node
def _simple_process(arg):
    global VERBOSE
    VERBOSE = True
    print(arg)

# Run module as a program - for testing/development only:
if __name__ == "__main__":
    print("TEST: Note that already seen types are skipped, and this is a depth-first search =>  The structure of the tree is not easily seen from this output.")
    walk_type_tree(ifex_ast.Namespace, _simple_process)

    x = ifex_ast.Typedef("name", datatype="variant<a,b>")
    print(f"{is_ifex_variant_shortform(x.datatype)=}")
    print(f"{is_ifex_variant_typedef(x)=}")

    y = ifex_ast.Typedef("name", datatypes=["foo", "bar", "baz"])
    print(f"{is_ifex_variant_shortform(y.datatype)=}")
    print(f"{is_ifex_variant_typedef(y)=}")
    print(f"The types of y are: {get_variant_types(y)}")
    print(f"The types of x are: {get_variant_types(x)}")
    s = "variant<this, that ,and,another >"
    print(f"The types of {s} are: {get_variant_types(s)}")
