# SPDX-License-Identifier: MPL-2.0
# ----------------------------------------------------------------------------
# (C) 2025 MBition GmbH
# Function to merge two trees (IFEX core IDL + overlay, or other layers)
# ----------------------------------------------------------------------------
# vim: sw=4 et

from dataclasses import fields, is_dataclass, replace
from models.common.ast_utils import ast_as_yaml
from models.ifex.ifex_ast import *
from models.ifex.ifex_parser import get_ast_from_yaml_file
from transformers.rule_translator import _log
from typing import List, Any, Type
import copy

def is_removal(name):
    """Check very simple rule:  Starts with '-' (minus) if it is a removal, '+' or none at all means adding"""
    return name is not None and name.startswith("-")


def name_only(name):
    """Remove preceeding +/- from type name"""
    if name is not None:
        return name.lstrip("-").lstrip("+")
    return None


# This merges lists of simple fields (list of strings)
def merge_field_list(list1: List[str], list2: List[str]) -> List[str]:
    merged = set(list1)
    for item in list2:
        name = name_only(item)
        if is_removal(item):
            if name in merged:
                merged.remove(name)
            else:
                # FIXME use better reporting
                _log("WARN", f"*** Warning: Overlay wants to remove {name=} but it didn't exist before")
        else:
            # Add to set even if it exists
            merged.add(name)

    return sorted(list(merged))  # Sort list because set has no guaranteed order


# This merges lists of AST objects, where we can expect there is a "name" field
def merge_object_lists(list1: List[Any], list2: List[Any]) -> List[Any]:
    """Merge two lists without duplicates based on the 'name' attribute."""

    # TODO - if it is a plain list of fields instead of complex items, then there is no item.name
    merged = {name_only(item.name): item for item in list1}

    for item in list2:
        name = name_only(item.name)
        if is_removal(item.name):
            if name in merged:
                del merged[name]
            else:
                # FIXME use better reporting
                _log("WARN", f"*** Warning: Overlay wants to remove {name=} but it didn't exist before")
        else:
            if name not in merged:
                # In the merge we want to remove all +/- if they are used, but for debugging
                # we print out the original overlay object.  Therefore, don't modify and
                # reference the overlay object - use a copy
                item_copy = copy.deepcopy(item)
                item_copy.name = name  # In merged tree only: remove +/- sign
                merged[name] = item_copy
            else:
                merged[name] = merge_nodes(merged[name], item)

    return list(merged.values())


def merge_nodes(node1: Any, node2: Any) -> Any:
    """Recursively merge two nodes."""
    if not is_dataclass(node1) or not is_dataclass(node2):
        return node2 or node1

    node_type = type(node1)
    merged_values = {}

    for var in [field.name for field in fields(node_type)]:
        value1 = getattr(node1, var, None)
        value2 = getattr(node2, var, None)

        # TODO Removal shall be possible on Lists, without object having a name
        # e.g. removal of type from datatypes: in a variant

        if isinstance(value1, list) and isinstance(value2, list):
            if len(value2) > 0:
                if is_dataclass(value2[0]):
                    merged_value = merge_object_lists(value1, value2)
                else:
                    merged_value = merge_field_list(value1, value2)
            else:  # value2 is empty list, so the merged result is simply value1
                merged_value = value1

        elif is_dataclass(value1) and is_dataclass(value2):
            if is_removal(value2.name):
                merged_value = None  # Not storing anything, so it's remmoved
            else:
                merged_value = merge_nodes(value1, name_only(value2))
        else: # value is a simple field.  Therefore if value2 is defined, it
              # overwrites the original value (there is no "merging" of two fundamental fields)
              # If value2 is not defined, the result defaults back to original value1
            merged_value = name_only(value2) or value1

        merged_values[var] = merged_value

    # (Dataclass function which replaces all member variables with new values:)
    return replace(node1, **merged_values)


def merge_asts(ast1: AST, ast2: AST) -> AST:
    """Merge two ASTs into one."""
    return merge_nodes(ast1, ast2)


# MAIN = Standalone test Code only, not normal use
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 2:
        file1 = sys.argv[1]
        file2 = sys.argv[2]
        ast1 = get_ast_from_yaml_file(file1)
        ast2 = get_ast_from_yaml_file(file2)
        merged_ast = merge_asts(ast1, ast2)
        print(ast_as_yaml(ast1))
        print("-----------------------------------------")
        print(ast_as_yaml(ast2))
        print("-----------------------------------------")
        print(ast_as_yaml(merged_ast))
        print("=========================================")
    else:
        m1 = Method(name="m1", input=[Argument(name="foo", datatype="int32")])

        m3 = Method(name="m3", input=[Argument(name="thisthat", datatype="int32")])
        m3.output = [Argument(name="my_out", datatype="string")]

        ns1 = Namespace(name="namespace1", methods=[Method(name="m2", returns=[Argument(name="retval")]), m1, m3])

        ast1 = AST(
            name="AST1",
            namespaces=[ns1, Namespace(name="namespace2")],
        )

        m1 = Method(name="m1", input=[Argument(name="foo", datatype="int32")])
        m1.output = [Argument(name="out", datatype="string")]

        # Test removal of retval
        m2 = Method(name="m2", returns=[Argument(name="-retval")])

        # Modify datatype of thisthat to string
        m3 = Method(name="m3", input=[Argument(name="thisthat", datatype="string")])
        m3.output = [Argument(name="my_out", datatype="string")]

        ast2 = AST(
            name="AST2",
            namespaces=[
                Namespace(name="namespace1", methods=[m1, m2, m3]),
                Namespace(name="namespace3"),
            ],
        )

        merged_ast = merge_asts(ast1, ast2)
        merged_ast.name = "Merged Result"

        print(ast_as_yaml(ast1))
        print("-----------------------------------------")
        print(ast_as_yaml(ast2))
        print("=========================================")
        print(ast_as_yaml(merged_ast))
