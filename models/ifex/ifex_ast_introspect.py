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

import models.ifex.ifex_ast as ifex_ast
import re

# ------------------------------------------------------------------------------------------------
# In ast_utils.py we have generic functions that give information about a AST-model built
# from a number of @dataclasses and field typing information.
# Those only refers to *python* concepts such as @dataclasses and the typing module.
# They can be used for other similarly described AST models, beyond the IFEX
# Core IDL model.
#
# In this file are some functions that are specific to IFEX. For example is_ifex_variant_typedef evaluates
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
