# SPDX-FileCopyrightText: Copyright (c) 2025 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project
# vim: tw=120 ts=4 et

"""
Parse an AIDL source file and build an AIDLFile AST.

Public API:
    get_ast_from_aidl_file(aidl_file: str) -> AIDLFile
        Read a .aidl file and return its AIDLFile AST.

    get_ast_from_aidl_text(text: str) -> AIDLFile
        Parse AIDL source text directly and return AIDLFile.

Design notes
------------
  1.  Comments are stripped from the source before Lark ever sees it.
  2.  Lark is run in LALR mode with the grammar in aidl.grammar.
  3.  The resulting lark.Tree / lark.Token tree is walked manually
      (destructively, using .children.pop(0)) to build typed AST
      objects defined in aidl_ast.py.

The Tree / Token data model (same as protobuf):

  Tree(data, children):
      .data     = Token('RULE', rule_name)   -- the grammar rule name
      .children = list of Tree or Token objects

  Token(type, value):
      .type  = uppercase terminal name from grammar (e.g. 'IDENT')
      .value = matched string

The same pattern-matching mini-framework is copied from protobuf_lark.py
so that the helper functions (assert_rule_match, assert_token, etc.) can
be reused verbatim.
"""

import lark
import os
import re
import sys

from lark import Lark, Tree, Token

from ifex.models.aidl import aidl_ast as aidl_model
from ifex.models.aidl.aidl_ast import (
    AIDLFile, Import, Interface, Method, Parameter, Const,
    Parcelable, ParcelableField, Enum, EnumElement,
)
from ifex.models.common.ast_utils import ast_as_yaml


# ============================================================
# Low-level helpers
# ============================================================

# Remove lines matching regexp
def filter_out(s, re_pattern):
    """Remove lines matching a regexp."""
    return '\n'.join([line for line in s.split('\n') if not re_pattern.match(line)])

# Remove partial lines matching regexp
def filter_out_partial(s, pattern):
    """Remove partial matches from each line."""
    return '\n'.join([re.sub(pattern, "", line) for line in s.split('\n')])

# Useful helpers
def is_tree(node):
    return type(node) is lark.Tree

def is_token(node):
    return type(node) is lark.Token

def truncate_string(s, maxlen=77):
    if len(s) > maxlen:
        return s[0:maxlen] + "..."
    return s

# ============================================================
# PATTERN MATCHING
#
# Here we build a set of functions that will take a pattern token-tree
# and compare it to the real token tree, to be able to recognize and extract
# features more easily.  For both the Tree and Token type, it is possible to
# specify the .children or .value to match against, or to pass a wildcard.
# (we use ['*'] for lists (children) and '*' for strings (value) to match
# any value therein.

# ============================================================

# String matcher which allows "*" = wildcard on the string we are comparing *to*!
def match_str(s1, s2):
    return s1 == s2 or s2 == "*"

# Checks that all objects in node-list match the corresponding pattern-list
def match_children(node_list, pattern_list):
    return (pattern_list == ['*'] or
            (len(node_list) == len(pattern_list) and
             all(matcher(x, y) for (x, y) in zip(node_list, pattern_list))))

# Match any node against a pattern - can use wildcard in the treepattern
# For Tree nodes, it will recurse and require the entire sub-tree to match.
def matcher(node, pattern):
    if type(node) is list:
        return (pattern is list and
                len(node) == len(pattern) and
                all(matcher(x, y) for (x, y) in zip(node, pattern)))
    elif is_tree(node):
        return (is_tree(pattern) and
                node.data == pattern.data and
                match_children(node.children, pattern.children))
    elif is_token(node):
        return (is_token(pattern) and
                match_str(node.type, pattern.type) and
                match_str(node.value, pattern.value))
    else:
        raise TypeError(f"Unknown type passed to matcher(): {type(node)}")


# Helper to extract a subtree of a certain type (as identified by the grammar rule name)
def get_items_of_type(node, grammar_rule_name):
    """Return all direct children of node whose rule name matches."""
    return [x for x in node.children
            if matcher(x, Tree(Token('RULE', grammar_rule_name), ['*']))]


# ============================================================
# ASSERTS - Functions to check that we have the expected format of the
# token-tree (Lark parser output).
#
# If we get invalid input then the parsing should _usually_ fail earlier
# according to the grammar rules.  In the rest of the program we should have
# the right understanding of which sequence of tokens is received and asserts
# are used to check this understanding.  If there is a mistake, these assert
# calls can help to catch it instead of passing invalid data to the next step.
# It is thus used primarily as a development tool.
#
# During development it is in other words possible that these will throw
# exception once in a while, to notify that something needs to be adjusted.

# ============================================================

# Error message helper
def create_error_message(node, pattern):
    node_string = truncate_string(f"{node!r}")
    pattern_string = truncate_string(f"{pattern!r}")
    return (f"\nPROBLEM: Failed expected match:\n"
            f"         - wanted pattern: {pattern_string}\n"
            f"         - item is: {node_string}")


# Raise exception if a node does not matches a pattern
def assert_match(node, pattern, error_message=None):
    if not matcher(node, pattern):
        if error_message is None:
            error_message = create_error_message(node, pattern)
        raise Exception(error_message)


# Check if the node is a tree representing a RULE of type "grammar_rule_name"
def rule_match(tree, grammar_rule_name):
    return matcher(tree, Tree(Token('RULE', grammar_rule_name), ['*']))


# Assert that the node is a tree representing a RULE of type "grammar_rule_name"
def assert_rule_match(tree, grammar_rule_name):
    assert_match(tree, Tree(Token('RULE', grammar_rule_name), ['*']))


# Assert that tree matches *at least one* of the named rules
def assert_rule_match_any(tree, grammar_rule_names):
    if not any(matcher(tree, Tree(Token('RULE', y), ['*'])) for y in grammar_rule_names):
        node_string = truncate_string(f"{tree!r}")
        raise Exception(
            f"PROBLEM: Failed expected match:\n"
            f"        - wanted one of {grammar_rule_names}\n"
            f"        - item is: {node_string}")


# Assert that node is a Token of the given type, optionally checking
# for specific data (or wildcard)
def assert_token(node, token_type, data_match='*'):
    assert_match(node, Token(token_type, data_match))


def assert_token_any(node, token_types, data_match='*'):
    if not any(matcher(node, Token(y, "*")) for y in token_types):
        node_string = truncate_string(f"{node!r}")
        raise Exception(
            f"PROBLEM: Failed expected token type(s):\n"
            f"        - wanted one of {token_types}\n"
            f"        - item is: {node_string}")


# ============================================================
# Comment stripping  (same approach as protobuf_lark.py)
# ============================================================

def filter_comments(text):
    # Remove full comment lines (// ...)
    text = filter_out(text, re.compile(r'^ *//'))
    # Remove inline trailing comments (// ...)
    text = filter_out_partial(text, r'//.*$')
    # Remove block comments (/* ... */)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    return text


# ============================================================
# AIDL-specific processing functions
# ============================================================

def process_type(t):
    """Extract the string representation of an aidl_type node.

    Grammar rule:  aidl_type: IDENT ARRAY_SUFFIX?

    Returns a string like "int", "String", "MyType", "int[]".
    """
    assert_rule_match(t, 'aidl_type')
    name_token = t.children.pop(0)
    assert_token(name_token, 'IDENT')
    type_str = name_token.value
    # Optional array suffix
    if t.children:
        suffix_token = t.children.pop(0)
        assert_token(suffix_token, 'ARRAY_SUFFIX')
        type_str += suffix_token.value
    return type_str


def process_param(p):
    """Process a param rule → Parameter.

    Grammar rule:  param: X_DIRECTION aidl_type IDENT
    """
    assert_rule_match(p, 'param')

    # 1. Direction
    dir_token = p.children.pop(0)
    assert_token(dir_token, 'X_DIRECTION')
    direction = dir_token.value

    # 2. Type
    type_node = p.children.pop(0)
    datatype = process_type(type_node)

    # 3. Name
    name_token = p.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    return Parameter(name=name, datatype=datatype, direction=direction)


def process_method(m):
    """Process a method_decl rule → Method.

    Grammar rule:  method_decl: X_ONEWAY? aidl_type IDENT "(" param_list? ")" ";"
    """
    assert_rule_match(m, 'method_decl')

    # 1. Optional oneway keyword
    oneway = False
    if m.children and is_token(m.children[0]) and m.children[0].type == 'X_ONEWAY':
        m.children.pop(0)
        oneway = True

    # 2. Return type
    type_node = m.children.pop(0)
    return_type = process_type(type_node)

    # 3. Method name
    name_token = m.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    # 4. Optional param_list
    params = []
    param_list_nodes = get_items_of_type(m, 'param_list')
    if param_list_nodes:
        pl = param_list_nodes[0]
        assert_rule_match(pl, 'param_list')
        for param_node in get_items_of_type(pl, 'param'):
            params.append(process_param(param_node))

    return Method(
        name=name,
        return_type=return_type,
        parameters=params if params else None,
        oneway=oneway,
    )


def process_const(c):
    """Process a const_decl rule → Const.

    Grammar rule:  const_decl: "const" aidl_type IDENT "=" CONST_VALUE ";"
    """
    assert_rule_match(c, 'const_decl')

    # 1. Type
    type_node = c.children.pop(0)
    datatype = process_type(type_node)

    # 2. Name
    name_token = c.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    # 3. Value
    value_token = c.children.pop(0)
    assert_token(value_token, 'CONST_VALUE')
    value = value_token.value.strip()

    return Const(name=name, datatype=datatype, value=value)


def process_interface(i):
    """Process an interface_decl rule → Interface.

    Grammar rule:
        interface_decl: X_ONEWAY? "interface" IDENT "{" interface_member* "}"
    """
    assert_rule_match(i, 'interface_decl')

    # 1. Optional interface-level oneway
    oneway = False
    if i.children and is_token(i.children[0]) and i.children[0].type == 'X_ONEWAY':
        i.children.pop(0)
        oneway = True

    # 2. Interface name
    name_token = i.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    # 3. Methods
    methods = []
    for node in get_items_of_type(i, 'method_decl'):
        methods.append(process_method(node))

    # 4. Consts
    consts = []
    for node in get_items_of_type(i, 'const_decl'):
        consts.append(process_const(node))

    return Interface(
        name=name,
        methods=methods if methods else None,
        consts=consts if consts else None,
        oneway=oneway,
    )


def process_field(f):
    """Process a field_decl rule → ParcelableField.

    Grammar rule:  field_decl: aidl_type IDENT ";"
    """
    assert_rule_match(f, 'field_decl')

    # 1. Type
    type_node = f.children.pop(0)
    datatype = process_type(type_node)

    # 2. Name
    name_token = f.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    return ParcelableField(name=name, datatype=datatype)


def process_parcelable(p):
    """Process a parcelable_decl rule → Parcelable.

    Grammar rule:
        parcelable_decl: "parcelable" IDENT "{" field_decl* "}"
    """
    assert_rule_match(p, 'parcelable_decl')

    # 1. Name
    name_token = p.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    # 2. Fields
    fields = []
    for node in get_items_of_type(p, 'field_decl'):
        fields.append(process_field(node))

    return Parcelable(
        name=name,
        fields=fields if fields else None,
    )


def process_enum_element(e):
    """Process an enum_element rule → EnumElement.

    Grammar rule:  enum_element: IDENT ("=" INT)? ","?
    """
    assert_rule_match(e, 'enum_element')

    # 1. Name
    name_token = e.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    # 2. Optional value
    value = None
    if e.children:
        value_token = e.children.pop(0)
        assert_token(value_token, 'INT')
        value = value_token.value

    return EnumElement(name=name, value=value)


def process_enum(e):
    """Process an enum_decl rule → Enum.

    Grammar rule:  enum_decl: "enum" IDENT "{" enum_element* "}"
    """
    assert_rule_match(e, 'enum_decl')

    # 1. Name
    name_token = e.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    # 2. Elements
    elements = []
    for node in get_items_of_type(e, 'enum_element'):
        elements.append(process_enum_element(node))

    return Enum(
        name=name,
        elements=elements if elements else None,
    )


def process_import(i):
    """Process an import_decl rule → Import.

    Grammar rule:  import_decl: "import" QUALNAME ";"
    """
    assert_rule_match(i, 'import_decl')

    path_token = i.children.pop(0)
    assert_token(path_token, 'QUALNAME')
    return Import(path=path_token.value)


def process_package(p):
    """Process a package_decl rule → str.

    Grammar rule:  package_decl: "package" QUALNAME ";"
    """
    assert_rule_match(p, 'package_decl')

    path_token = p.children.pop(0)
    assert_token(path_token, 'QUALNAME')
    return path_token.value


# ============================================================
# Top-level tree processor
# ============================================================

def process_lark_tree(root):
    """Walk the root lark.Tree and build an AIDLFile AST.

    Grammar rule:  aidl_file: package_decl import_decl* declaration
    """
    assert_rule_match(root, 'aidl_file')

    # 1. Package (exactly one)
    package_nodes = get_items_of_type(root, 'package_decl')
    if len(package_nodes) != 1:
        raise Exception(f"Expected exactly one package declaration, found {len(package_nodes)}")
    package = process_package(package_nodes[0])

    # 2. Imports (zero or more)
    imports = []
    for node in get_items_of_type(root, 'import_decl'):
        imports.append(process_import(node))

    # 3. Declaration (exactly one: interface, parcelable, or enum)
    interface_nodes   = get_items_of_type(root, 'interface_decl')
    parcelable_nodes  = get_items_of_type(root, 'parcelable_decl')
    enum_nodes        = get_items_of_type(root, 'enum_decl')

    total = len(interface_nodes) + len(parcelable_nodes) + len(enum_nodes)
    if total != 1:
        raise Exception(
            f"Expected exactly one top-level declaration (interface/parcelable/enum), found {total}")

    if interface_nodes:
        declaration = process_interface(interface_nodes[0])
    elif parcelable_nodes:
        declaration = process_parcelable(parcelable_nodes[0])
    else:
        declaration = process_enum(enum_nodes[0])

    return AIDLFile(
        package=package,
        declaration=declaration,
        imports=imports if imports else None,
    )


# ============================================================
# Grammar loading and parsing
# ============================================================

def _load_grammar() -> str:
    """Load the AIDL Lark grammar from the models/aidl directory."""
    grammar_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'aidl.grammar')
    with open(grammar_file, 'r') as f:
        return f.read()


def parse_text(text: str) -> AIDLFile:
    """Parse AIDL source text and return an AIDLFile AST."""
    grammar = _load_grammar()
    parser = Lark(grammar, parser='lalr')
    clean = filter_comments(text)
    tree = parser.parse(clean)
    return process_lark_tree(tree)


def read_aidl_file(aidl_file: str) -> str:
    """Read an AIDL source file and strip comments."""
    with open(aidl_file, 'r') as f:
        return filter_comments(f.read())


# ============================================================
# Public entry point
# ============================================================

def get_ast_from_aidl_file(aidl_file: str) -> AIDLFile:
    """Read a .aidl file and return its AIDLFile AST.

    :param aidl_file: path to a .aidl source file
    :return: AIDLFile abstract syntax tree
    """
    text = read_aidl_file(aidl_file)
    grammar = _load_grammar()
    parser = Lark(grammar, parser='lalr')
    tree = parser.parse(text)
    return process_lark_tree(tree)


# ============================================================
# Script entry point
# ============================================================

if __name__ == '__main__':
    ast = get_ast_from_aidl_file(sys.argv[1])
    print(ast_as_yaml(ast))
