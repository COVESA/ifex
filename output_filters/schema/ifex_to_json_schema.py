# SPDX-License-Identifier: MPL-2.0

# =======================================================================
# (C) 2023 MBition GmbH
# Author: Gunnar Andersson
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# =======================================================================

"""
Generate JSON Schema equivalent to the python-internal model definition.
"""

from dataclasses import fields
from datetime import datetime, date

from models.ifex.ifex_ast_construction import is_simple_type

from models.ifex.ifex_ast import AST
from models.ifex.ifex_ast_introspect import actual_type, field_actual_type, field_inner_type, inner_type, is_forwardref, is_list, type_name, field_is_list, field_is_optional, field_referenced_type
from typing import Any
import json

# =======================================================================
# Helpers
# (Most general ones are in ifex_ast_introspect module instead)
# =======================================================================

# This function is local because "string" and "integer" are neither python
# or IFEX types -- it is the way JSON-schema spells them
def get_type_name(t):
    if t is Any:
        return "Any"
    if t is bool:
        return "boolean"
    elif t is datetime:
        return "string"
    elif t is date:
        return "string"
    elif t is str:
        return "string"
    elif t is int:
        return "integer"
    elif t is float:
        return "number"
    else: # "complex type"
        return type_name(actual_type(t))

# =======================================================================
# JSON SCHEMA OUTPUT
# =======================================================================

# Here are print-functions for the main object type variations in the JSON
# schema such as a single object, or an array of objects.

# Special case for "Any" (used with Option values). For now we allow it to be
# either an integer or a string when checking against a schema.  Many languages
# assume enum value to be only represented by integers, but IFEX **in theory**
# allows _any_ data type for enumerations, and thus any value of that type.
# However, in YAML it seems, for now, only realistic to allow specifying
# constant values as either numbers and strings.

def print_field(field_name, type_name, is_primitive=False, description=None):
    if type_name == 'Any':
        # For now, considered to be *either* a number or string.
        print(f'"{field_name}" : {{ "anyOf": [\n {{ "type": "integer" }},\n {{ "type": "string" }}\n]\n', end="")
    elif is_primitive:
        print(f'"{field_name}" : {{ "type": "{type_name}"\n', end="")
    else:  # complex/object type
        print(f'"{field_name}" : {{ "type": "object",\n"$ref": "#/definitions/{type_name}"\n', end="")
    if description:
        print(f', "description": "{description}"')
    print('}')

def print_array_field(field_name, type_name, is_primitive=False, description=None):
    if type_name == 'Any':
        print(f'"{field_name}" : {{ "type": "array", "items": {{ "anyOf": [\n {{ "type": "integer" }},\n {{ "type": "string"}}\n]\n}}', end="")
    elif is_primitive:
        print(f'"{field_name}" : {{ "type": "array", "items": {{ "type": "{type_name}" }}')
    else:
        print(f'"{field_name}" : {{ "type": "array", "items": {{ "$ref": "#/definitions/{type_name}" }}')
    if description:
        print(f', "description": "{description}"') 
    print('}')

def print_type(t, fields):
    print(f'"{t}": {{ "type": "object", "properties": {{')
    for n, (field_name, field_type, is_array, _) in enumerate(fields):
        # FIXME add description to print_field
        is_primitive = (get_type_name(field_type) in ["string", "integer"])
        if is_array:
            print_array_field(field_name, get_type_name(field_type), is_primitive)
        else:
            print_field(field_name, get_type_name(field_type), is_primitive)
        # Skipping last comma - is there a better idiom for this?  Probably.
        if n != len(fields)-1:
            print(',')
    print('},')

    # Same loop for the "required" field
    print(f'"required" : [')
    for n, (field_name, field_type, is_array, is_required) in enumerate(fields):
        if is_required:
            # Comma, if there were any previous ones
            if n != 0:
                print(',')
            print(f'"{field_name}"', end="")

    print(f'],')
    print('"additionalProperties" : false') 

# =======================================================================
# Model traversal
# =======================================================================

def collect_type_info(t, collection={}, seen={}):
    """This is the main recursive function that loops through tree and collects
       information about its structure which is later used to output the schema:"""

    # We don't need to gather information about primitive types because they
    # will not have any member fields below them.
    if is_simple_type(t) or t is Any:
        return

    # ForwardRef will fail if we try to recurse over its children.  However,
    # the types that are handled with ForwardRef (Namespace) ought to appear
    # anyhow *somewhere else* in the tree as a real type -> so we can skip it.
    if is_forwardref(t):
        return

    # Also skip types we have already seen because the tree search will
    # encounter duplicates
    typename = type_name(t)
    if seen.get(typename):
        return

    seen[typename] = True

    # From here, we know it is a composite type (a dataclass from ifex_ast.py)
    # Process each of its member fields, remembering the name and type of each so that
    # that can be printed to the JSON schema
    for f in fields(t):
        field_name = f.name
        field_type = field_referenced_type(f)

        # Define each type by storing each of its fields and those fields' types.
        # We should also remember if it is a collection/list (in JSON-schema called array)
        if not collection.get(typename):
            collection[typename] = []
        collection[typename].append((field_name, field_type, field_is_list(f), not field_is_optional(f)))

        # Self recursion on the type of each found member field
        collect_type_info(field_type, collection, seen)


# =======================================================================
# MAIN PROGRAM
# =======================================================================

if __name__ == "__main__":

    # First, collect info
    types={}
    collect_type_info(AST, types)

    # Then print JSON-schema
    print('''{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "IFEX Core IDL (YAML format), version: TAG-PLACEHOLDER",
    "description": "This file can be used to validate IFEX Core IDL files, which are normally written in YAML, not JSON.  The schema is not the source-of-truth but an artifact generated from the source-of-truth, so it should be consistent",
    "type": "object",
    "allOf": [ { "$ref": "#/definitions/AST" } ],
    "definitions": {
    ''')

    items=types.items()
    for n, (typ,fields) in enumerate(items):
        print_type(typ, fields)
        # print comma, but not on last item
        if n != len(items)-1:
            print('},')
        else:
            print('}')
    print('}\n}')

