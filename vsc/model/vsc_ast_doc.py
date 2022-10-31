# SPDX-License-Identifier: MPL-2.0

# (C) 2022 Novaspring AB
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Generate documentation of the AST structure from the structure
itself (the content of the defined @dataclasses)
"""

from dataclasses import fields
from typing import Union, get_origin, get_args
from vsc.model.vsc_ast import Namespace


#
# These helper functions determine the type of object, or they coerce
# special case handling into a simpler expression that can be used in later
# functions.
#

# typing.Optional?
def is_optional(field):
    return get_origin(field) is Union and type(None) in get_args(field)


# typing.ForwardRef?
def is_forwardref(field):
    return type(field).__name__ == 'ForwardRef'


# typing.List[<something>]? (also Optional[List[<something>]])
def is_list(field):
    if field.type in [str, int]:
        return False
    else:
        # (I would prefer to compare types here with "is" or issubclass() or
        # similar, instead of comparing strings but this is so far the way I
        # found to make the test:
        return actual_type(field).__name__ == 'List'


# This takes care about the fact that ForwardRef does not have
# a member __name__ (because it's not actually a type, as such)
# Instead it has __forward_arg__ which is a string containing
# the referenced type name.
def type_name(ttype):
    if is_forwardref(ttype):
        return ttype.__forward_arg__
    else:
        return ttype.__name__


# This strips off Optional[] from the type hierarchy so that we are left
# with the "real" inner type.  (It can still be a List of Something)
def actual_type(field):
    if type(field) in [str, int]:
        return type(field)
    if is_optional(field.type):
        return get_args(field.type)[0]
    else:
        return field.type


def actual_type_name(field):
    return type_name(actual_type(field))


# Return the type of members of a List
# Only call if it is already known to be a List.
def list_member_type(field):
    return get_args(actual_type(field))[0]


def list_member_type_name(field):
    return type_name(list_member_type(field))



#
# Document generation functions
#


def markdown_heading(n: int, s: str):
    for _ in range(n):
        print("#", end='')
    print(f" {s}")
    print()


def markdown_table_row(field):
    print(f"| {field.name} | ", end='')
    if field.type is str:
        print("A single **str**", end='')
    elif is_list(field):
        print(f"A list of **{list_member_type_name(field)}**_s_", end='')
    else:
        print(f"A single **{actual_type_name(field)}**", end='')
    print(" |")


def markdown_table(fields):
   print(f"|Field Name|Required contents|")
   print(f"|-----|-----------|")
   for f in fields:
       markdown_table_row(f)

def document_fields(node):
    name = type_name(node)
    markdown_heading(2, name)

    markdown_heading(4, f"Mandatory fields for {name}:")
    markdown_table([x for x in fields(node) if not is_optional(x.type)])
    print()
    markdown_heading(4, f"Optional fields for {name}:")
    markdown_table([x for x in fields(node) if is_optional(x.type)])
    print("\n")


def walk_type_tree(node, process, seen={}):
    """Walk the AST class hierarchy as defined by @dataclasses with type
    hints from typing module.

    Performs a depth-first traversal where parent node is processed, then
    its children, going as deep as possible before backtracking.

    Arguments: node = a @dataclass class
               process = function to call for each node"""

    if node in [str, int]: # (No need to document, or recurse on these)
        return

    # Skip duplicates (like Namespace, it appears more than once in AST model)
    name = type_name(node)
    if seen.get(name):
        return

    process(node)
    seen[name] = True

    # Recurse on each AST type used in child fields (stripping
    # away 'List' and 'Optional' to get to the interesting class)
    for n in fields(node):
        if is_list(n):
            # Document Node types that are found inside Lists
            walk_type_tree(list_member_type(n), process, seen)
        else:
            # Document Node types found directly
            walk_type_tree(actual_type(n), process, seen)


if __name__ == "__main__":
    walk_type_tree(Namespace, document_fields)


