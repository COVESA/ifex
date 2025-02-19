# SPDX-License-Identifier: MPL-2.0
# ----------------------------------------------------------------------------
# (C) 2025 MBition GmbH
# Function to merge two trees (IFEX core IDL + overlay, or other layers)
# ----------------------------------------------------------------------------
# vim: sw=4 et

from dataclasses import fields, is_dataclass, replace
from models.ifex.ifex_ast import *
from models.ifex.ifex_ast_construction import ifex_ast_as_yaml
from models.ifex.ifex_parser import get_ast_from_yaml_file
from typing import List, Any, Type
import copy

def is_removal(name):
   """Check very simple rule:  Starts with '-' (minus) means removal, '+' or none at all means adding"""
   return name is not None and name.startswith("-")

def name_only(name):
   """Remove preceeding +/- from type name"""
   if name is not None:
       return name.lstrip('-').lstrip('+')
   return None

def merge_field_list(list1: List[str], list2: List[str]) -> List[str]:
    """This merges lists of simple fields (list of strings)"""
    merged = set(list1)
    for item in list2:
        name = name_only(item)
        if is_removal(item):
            if name in merged:
                merged.remove(name)
            else:
                # FIXME use better reporting
                print(f"*** Warning: Overlay wants to remove {name=} but it didn't exist before")
        else:
            # Add to set even if it exists
            merged.add(name)

    return sorted(list(merged)) # Sort list because set has no guaranteed order

# Merges lists of AST objects where we can expect there is a "name" field
def merge_object_lists(list1: List[Any], list2: List[Any]) -> List[Any]:
    """Merge two _lists_ of AST objects, without duplicates based on the 'name' attribute."""

    # TODO - if it is a plain list of fields instead of complex items, then there is no item.name
    merged = {name_only(item.name): item for item in list1}

    for item in list2:
        name = name_only(item.name)
        if is_removal(item.name):
            if name in merged:
                del merged[name]
            else:
                # FIXME use better reporting
                print(f"*** Warning: Overlay wants to remove {name=} but it didn't exist before")
        else:
            if name not in merged:
                # In the merge we want to remove all +/- if they are used, but for debugging
                # we print out the original overlay object.  Therefore, don't modify and 
                # reference the overlay object - use a copy
                item_copy = copy.deepcopy(item)
                item_copy.name = name   # In merged tree only: remove +/- sign
                merged[name] = item_copy
            else:
                merged[name] = merge_nodes(merged[name], item)

    return list(merged.values())


def merge_nodes(node1: Any, node2: Any) -> Any:
    """Recursively merge two trees, represented by their root nodes."""
    if not is_dataclass(node1) or not is_dataclass(node2):
        return node2 or node1

    node_type = type(node1)
    merged_values = {}

    for field_name in [field.name for field in fields(node_type)]:
        value1 = getattr(node1, field_name, None)
        value2 = getattr(node2, field_name, None)

        # TODO Removal shall be possible on Lists, without object having a name
        # e.g. removal of type from datatypes: in a variant

        # For lists, each object is compared by name to see if the overlay shall
        # apply (recursion down the tree as usual).  New objects that don't
        # match an old one are added to the end of the list
        if isinstance(value1, list) and isinstance(value2, list):
            if len(value2) > 0:
                if is_dataclass(value2[0]):
                    merged_value = merge_object_lists(value1, value2)
                else:
                    merged_value = merge_field_list(value1, value2)
            else: # value2 is empty list
                merged_value = value1

        # For fields that refer to another complex object
        # Check if it is a node removal (=> assigning value = None), otherwise
        # continue merging by recursion on the referred object.
        elif is_dataclass(value1) and is_dataclass(value2):
            if is_removal(value2.name):
                merged_value = None
            else:
                merged_value = merge_nodes(value1, name_only(value2))

        # At the leaf-nodes, essentially. Fields that refer to a plain value - the
        # old value gets replaced if a new value was defined.
        else:
            merged_value = name_only(value2) or value1 # If value2 is defined, it overwrites value1

        # Storing the collection of resulting fields for this object:
        merged_values[field_name] = merged_value

    # In one go, replace all values with the new (or sometimes unchanged) ones:
    return replace(node1, **merged_values)


# Intended as public function
def merge_asts(ast1: AST, ast2: AST) -> AST:
    """Merge two ASTs into one."""
    return merge_nodes(ast1, ast2)

# MAIN = Standalone test Code only, not normal use
if __name__ == '__main__':
    import sys

    if len(sys.argv) > 2:
        file1 = sys.argv[1]
        file2 = sys.argv[2]
        ast1 = get_ast_from_yaml_file(file1)
        ast2 = get_ast_from_yaml_file(file2)
        merged_ast = merge_asts(ast1, ast2)
        print(ifex_ast_as_yaml(ast1))
        print ("-----------------------------------------")
        print(ifex_ast_as_yaml(ast2))
        print ("-----------------------------------------")
        print(ifex_ast_as_yaml(merged_ast))
        print ("=========================================")
    else:
        m1=Method(name="m1", input=[Argument(name="foo", datatype="int32")])
        ns1=Namespace(name="namespace1", methods=[Method(name="m2"), m1])
        ast1 = AST(
                name="AST1",
                namespaces=[ns1, Namespace(name="namespace2")],
                )

        m2=Method(name="m1", input=[Argument(name="foo", datatype="int32")])
        m2.output=[Argument(name="out", datatype="string")]

        ast2 = AST(
                name="AST2",
                namespaces=[Namespace(name="namespace1", methods=[m2]), Namespace(name="namespace3")]
                )

        merged_ast = merge_asts(ast1, ast2)
        merged_ast.name = "Merged Result"

        print(ifex_ast_as_yaml(ast1))
        print ("-----------------------------------------")
        print(ifex_ast_as_yaml(ast2))
        print ("=========================================")
        print(ifex_ast_as_yaml(merged_ast))
