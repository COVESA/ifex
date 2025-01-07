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
from models.ifex.ifex_ast import Namespace
from models.ifex.ifex_ast_introspect import walk_type_tree, field_is_list, is_optional, type_name, field_actual_type, field_inner_type
import re,itertools

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
    elif field_is_list(field):
        print(f"A list of **{type_name(field_inner_type(field))}**_s_", end='')
    else:
        print(f"A single **{type_name(field_actual_type(field))}**", end='')

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
   print(f"|Field Name|Contents|")
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


if __name__ == "__main__":
    walk_type_tree(Namespace, document_fields)

