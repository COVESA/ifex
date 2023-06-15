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
from ifex.model.ifex_ast import Namespace
import re, itertools

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

    print(docstring(field), end='')
    print(" |")

def determine_indentation(s):
    count = 0
    # groupby() will collect up repeating characters (like space) so we can
    # then count the number of spaces to know the indentation.
    for group in itertools.groupby(s):
        char = group[0]
        count = sum(1 for _ in group[1])
        # NOTE that the string can start with '\n', for example, so instead
        # of taking the first line we must iterate UNTIL the first indented
        # line is found.
        if char == '\t':
            raise Exception("""Sorry, TABS are not supported by the the
                    indentation detection code of the documentation
                    generator!""")
        # Keep looping until the first group of spaces
        if char == ' ':
            break
    return count

def docstring(item):

    # We can't remove all whitespace at start of every line because this
    # ruins the indentation of preformatted code blocks.  Instead, figure
    # out what the indentation level is on the first indented line of the
    # string, and remove that from all lines:

    s = item.__doc__
    if s is not None:
        n = determine_indentation(s)

        # Make a regexp that matches exactly 'n' number of spaces, at the
        # start of a line, and make sure it is set for multiple lines when
        # we then use it to substitute
        p1 = re.compile(f"^ {{{n}}}", re.MULTILINE)
        # Substitute with empty string, i.e. delete 'n' number of spaces
        return re.sub(p1, '', s)
    else:
        return ""

def markdown_table(fields):
   print(f"|Field Name|Required contents|")
   print(f"|-----|-----------|")
   for f in fields:
       markdown_table_row(f)

def document_fields(node):
    name = type_name(node)

    print('----') # Separator
    markdown_heading(2, name)

    print(docstring(node))

    markdown_heading(4, f"Mandatory fields for {name}:")
    markdown_table([x for x in fields(node) if not is_optional(x.type)])
    print()
    markdown_heading(4, f"Optional fields for {name}:")
    markdown_table([x for x in fields(node) if is_optional(x.type)])
    print("\n")


import typing
def walk_type_tree(node, process, seen={}):
    """Walk the AST class hierarchy as defined by @dataclasses with type
    hints from typing module.

    Performs a depth-first traversal.  Parent node is processed first, then its
    children, going as deep as possible before backtracking. Node names that have
    already been seen before are identical so recursion is cut off there. 
    The given hook function "process" is called for every unique node.

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

    # Next, recurse on each AST type used in child fields (stripping
    # away 'List' and 'Optional' to get to the interesting class)

    if is_forwardref(node):
        # WARNING: ForwardRef only gives us the class name, instead of the
        # actual class object.  For the purpose of listing all node types
        # there "should" be no problem to skip over this one, because it
        # should appear elsewhere in the tree, but this limitation should be known.
        pass
    else:
        for n in fields(node):
            if is_list(n):
                # Document Node types that are found inside Lists
                walk_type_tree(list_member_type(n), process, seen)
            else:
                # Document Node types found directly
                walk_type_tree(actual_type(n), process, seen)


if __name__ == "__main__":
    walk_type_tree(Namespace, document_fields)


