# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project
# vim: tw=120 ts=4 et

"""
Parse an OMG IDL source file and build an IDLFile AST.

Public API:
    get_ast_from_idl_file(idl_file: str) -> IDLFile
        Read a .idl file and return its IDLFile AST.

    get_ast_from_idl_text(text: str) -> IDLFile
        Parse IDL source text directly and return IDLFile.

Design notes
------------
Identical approach to aidl_lark.py / protobuf_lark.py:

  1.  Preprocessor lines (#include, #pragma, ...) and comments
      (// and /* */) are stripped from the source before Lark sees it.
  2.  Lark is run in LALR mode with the grammar in omgidl.grammar.
  3.  The resulting lark.Tree / lark.Token tree is walked manually
      (destructively, using .children.pop(0)) to build typed AST
      objects defined in omgidl_ast.py.

The Tree / Token data model (same as aidl_lark / protobuf_lark):

  Tree(data, children):
      .data     = Token('RULE', rule_name)
      .children = list of Tree or Token objects

  Token(type, value):
      .type  = uppercase terminal name from grammar
      .value = matched string

The same pattern-matching mini-framework from aidl_lark.py is copied
verbatim so assert_rule_match, assert_token, get_items_of_type etc.
are available with identical semantics.
"""

import lark
import os
import re
import sys

from lark import Lark, Tree, Token

from ifex.models.omgidl import omgidl_ast as omgidl_model
from ifex.models.omgidl.omgidl_ast import (
    IDLFile, Module, Interface, Operation, Attribute, Const,
    Parameter, Struct, Enum, Enumerator, Exception_, Typedef, Member,
)
from ifex.models.common.ast_utils import ast_as_yaml


# ============================================================
# Low-level helpers  (identical to aidl_lark.py)
# ============================================================

def filter_out(s, re_pattern):
    """Remove lines matching a regexp."""
    return '\n'.join([line for line in s.split('\n') if not re_pattern.match(line)])


def filter_out_partial(s, pattern):
    """Remove partial matches from each line."""
    return '\n'.join([re.sub(pattern, "", line) for line in s.split('\n')])


def is_tree(node):
    return type(node) is lark.Tree


def is_token(node):
    return type(node) is lark.Token


def truncate_string(s, maxlen=77):
    if len(s) > maxlen:
        return s[0:maxlen] + "..."
    return s


# ============================================================
# Pattern-matching framework  (identical to aidl_lark.py)
# ============================================================

def match_str(s1, s2):
    return s1 == s2 or s2 == "*"


def match_children(node_list, pattern_list):
    return (pattern_list == ['*'] or
            (len(node_list) == len(pattern_list) and
             all(matcher(x, y) for (x, y) in zip(node_list, pattern_list))))


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


def get_items_of_type(node, grammar_rule_name):
    """Return all direct children of node whose rule name matches."""
    return [x for x in node.children
            if matcher(x, Tree(Token('RULE', grammar_rule_name), ['*']))]


# ============================================================
# Assert helpers  (identical to aidl_lark.py)
# ============================================================

def create_error_message(node, pattern):
    return (f"\nPROBLEM: Failed expected match:\n"
            f"         - wanted pattern: {truncate_string(repr(pattern))}\n"
            f"         - item is: {truncate_string(repr(node))}")


def assert_match(node, pattern, error_message=None):
    if not matcher(node, pattern):
        if error_message is None:
            error_message = create_error_message(node, pattern)
        raise Exception(error_message)


def rule_match(tree, grammar_rule_name):
    return matcher(tree, Tree(Token('RULE', grammar_rule_name), ['*']))


def assert_rule_match(tree, grammar_rule_name):
    assert_match(tree, Tree(Token('RULE', grammar_rule_name), ['*']))


def assert_rule_match_any(tree, grammar_rule_names):
    if not any(matcher(tree, Tree(Token('RULE', y), ['*'])) for y in grammar_rule_names):
        raise Exception(
            f"PROBLEM: Failed expected match:\n"
            f"        - wanted one of {grammar_rule_names}\n"
            f"        - item is: {truncate_string(repr(tree))}")


def assert_token(node, token_type, data_match='*'):
    assert_match(node, Token(token_type, data_match))


def assert_token_any(node, token_types, data_match='*'):
    if not any(matcher(node, Token(y, "*")) for y in token_types):
        raise Exception(
            f"PROBLEM: Failed expected token type(s):\n"
            f"        - wanted one of {token_types}\n"
            f"        - item is: {truncate_string(repr(node))}")


# ============================================================
# Preprocessor and comment stripping
# ============================================================

def filter_preprocessor(text):
    """Strip C preprocessor lines (#include, #pragma, #define, etc.)."""
    return filter_out(text, re.compile(r'^ *#'))


def filter_comments(text):
    """Strip C/C++ style comments."""
    # Remove full comment lines
    text = filter_out(text, re.compile(r'^ *//'))
    # Remove inline trailing comments
    text = filter_out_partial(text, r'//.*$')
    # Remove block comments
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    return text


def preprocess(text):
    """Apply all pre-parse text transformations."""
    text = filter_comments(text)
    text = filter_preprocessor(text)
    return text


# ============================================================
# Type extraction helpers
# ============================================================

def process_type(t):
    """Extract the string representation of a type_spec node.

    Handles three grammar aliases:
      builtin_array_type: BUILTIN_TYPE ARRAY_SUFFIX?
      named_array_type:   IDENT ARRAY_SUFFIX?
      sequence_type:      "sequence" "<" (BUILTIN_TYPE|IDENT) ["," INT] ">"

    Returns a string like "long", "float[3]", "sequence<float>",
    "sequence<ClimateZone,10>", "ClimateZone".
    """
    assert_rule_match_any(t, ['builtin_array_type', 'named_array_type', 'sequence_type'])

    rule_name = t.data.value  # Token('RULE', name).value

    if rule_name == 'sequence_type':
        elem_token = t.children.pop(0)
        assert_token_any(elem_token, ['BUILTIN_TYPE', 'IDENT'])
        type_str = f"sequence<{elem_token.value}"
        if t.children:
            bound_token = t.children.pop(0)
            assert_token(bound_token, 'INT')
            type_str += f",{bound_token.value}"
        type_str += ">"
        return type_str

    # builtin_array_type or named_array_type
    name_token = t.children.pop(0)
    assert_token_any(name_token, ['BUILTIN_TYPE', 'IDENT'])
    type_str = name_token.value
    if t.children:
        suffix_token = t.children.pop(0)
        assert_token(suffix_token, 'ARRAY_SUFFIX')
        type_str += suffix_token.value
    return type_str


def process_scoped_name(node):
    """Extract a scoped_name node to a '::'-joined string."""
    assert_rule_match(node, 'scoped_name')
    parts = [tok.value for tok in node.children if is_token(tok) and tok.type == 'IDENT']
    # Handle leading '::' (global scope) — kept as-is
    leading = '::' if (node.children and is_token(node.children[0])
                       and node.children[0].type == '__ANON_0') else ''
    return leading + '::'.join(parts)


# ============================================================
# Processing functions — one per grammar rule
# ============================================================

def process_member(m):
    """Process a member_decl rule → Member.

    Grammar rule:  member_decl: type_spec IDENT ";"
    """
    assert_rule_match(m, 'member_decl')

    type_node = m.children.pop(0)
    datatype = process_type(type_node)

    name_token = m.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    return Member(name=name, datatype=datatype)


def process_param(p):
    """Process a param rule → Parameter.

    Grammar rule:  param: X_DIRECTION type_spec IDENT
    """
    assert_rule_match(p, 'param')

    dir_token = p.children.pop(0)
    assert_token(dir_token, 'X_DIRECTION')
    direction = dir_token.value

    type_node = p.children.pop(0)
    datatype = process_type(type_node)

    name_token = p.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    return Parameter(name=name, datatype=datatype, direction=direction)


def process_raises(r):
    """Process a raises_clause rule → List[str].

    Grammar rule:  raises_clause: "raises" "(" scoped_name ("," scoped_name)* ")"
    """
    assert_rule_match(r, 'raises_clause')
    names = []
    for node in get_items_of_type(r, 'scoped_name'):
        names.append(process_scoped_name(node))
    return names


def process_operation(o):
    """Process an operation_decl rule → Operation.

    Grammar rule:
        operation_decl: X_ONEWAY? op_return_type IDENT "(" param_list? ")" raises_clause? ";"
    """
    assert_rule_match(o, 'operation_decl')

    # 1. Optional oneway
    oneway = False
    if o.children and is_token(o.children[0]) and o.children[0].type == 'X_ONEWAY':
        o.children.pop(0)
        oneway = True

    # 2. Return type (void_return or typed_return)
    ret_node = o.children.pop(0)
    assert_rule_match_any(ret_node, ['void_return', 'typed_return'])
    if rule_match(ret_node, 'void_return'):
        return_type = 'void'
    else:
        return_type = process_type(ret_node.children[0])

    # 3. Operation name
    name_token = o.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    # 4. Optional parameter list
    params = []
    for pl in get_items_of_type(o, 'param_list'):
        for p in get_items_of_type(pl, 'param'):
            params.append(process_param(p))

    # 5. Optional raises clause
    raises = None
    raises_nodes = get_items_of_type(o, 'raises_clause')
    if raises_nodes:
        raises = process_raises(raises_nodes[0])

    return Operation(
        name=name,
        return_type=return_type,
        parameters=params if params else None,
        raises=raises,
        oneway=oneway,
    )


def process_attribute(a):
    """Process an attribute_decl rule → Attribute.

    Grammar rule:  attribute_decl: X_READONLY? "attribute" type_spec IDENT ";"
    """
    assert_rule_match(a, 'attribute_decl')

    # 1. Optional readonly
    readonly = False
    if a.children and is_token(a.children[0]) and a.children[0].type == 'X_READONLY':
        a.children.pop(0)
        readonly = True

    # 2. Type
    type_node = a.children.pop(0)
    datatype = process_type(type_node)

    # 3. Name
    name_token = a.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    return Attribute(name=name, datatype=datatype, readonly=readonly)


def process_const(c):
    """Process a const_dcl rule → Const.

    Grammar rule:  const_dcl: "const" type_spec IDENT "=" CONST_VALUE ";"
    """
    assert_rule_match(c, 'const_dcl')

    type_node = c.children.pop(0)
    datatype = process_type(type_node)

    name_token = c.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    value_token = c.children.pop(0)
    assert_token(value_token, 'CONST_VALUE')
    value = value_token.value.strip()

    return Const(name=name, datatype=datatype, value=value)


def process_struct(s):
    """Process a struct_decl rule → Struct.

    Grammar rule:  struct_decl: "struct" IDENT "{" member_decl+ "}" ";"
    """
    assert_rule_match(s, 'struct_decl')

    name_token = s.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    members = [process_member(m) for m in get_items_of_type(s, 'member_decl')]

    return Struct(name=name, members=members if members else None)


def process_exception(e):
    """Process an exception_decl rule → Exception_.

    Grammar rule:  exception_decl: "exception" IDENT "{" member_decl* "}" ";"
    """
    assert_rule_match(e, 'exception_decl')

    name_token = e.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    members = [process_member(m) for m in get_items_of_type(e, 'member_decl')]

    return Exception_(name=name, members=members if members else None)


def process_enum(e):
    """Process an enum_decl rule → Enum.

    Grammar rule:  enum_decl: "enum" IDENT "{" IDENT ("," IDENT)* "}" ";"

    Note: OMG IDL enumerators are identifiers only — no explicit integer
    values.  Values are implicitly 0, 1, 2, ... in declaration order.
    """
    assert_rule_match(e, 'enum_decl')

    # First IDENT is the enum name; remaining IDENTs are enumerators.
    tokens = [tok for tok in e.children if is_token(tok) and tok.type == 'IDENT']

    name = tokens[0].value
    enumerators = [Enumerator(name=tok.value) for tok in tokens[1:]]

    return Enum(name=name, enumerators=enumerators if enumerators else None)


def process_typedef(t):
    """Process a typedef_decl rule → Typedef.

    Grammar rule:  typedef_decl: "typedef" type_spec IDENT ";"
    """
    assert_rule_match(t, 'typedef_decl')

    type_node = t.children.pop(0)
    datatype = process_type(type_node)

    name_token = t.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    return Typedef(name=name, datatype=datatype)


def process_interface(i):
    """Process an interface_decl rule → Interface.

    Grammar rule:
        interface_decl: "interface" IDENT inheritance_spec? "{" interface_member* "}" ";"
    """
    assert_rule_match(i, 'interface_decl')

    # 1. Name
    name_token = i.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    # 2. Optional inheritance
    inherits = None
    inh_nodes = get_items_of_type(i, 'inheritance_spec')
    if inh_nodes:
        inh = inh_nodes[0]
        inherits = [process_scoped_name(sn) for sn in get_items_of_type(inh, 'scoped_name')]

    # 3. Operations
    operations = [process_operation(o) for o in get_items_of_type(i, 'operation_decl')]

    # 4. Attributes
    attributes = [process_attribute(a) for a in get_items_of_type(i, 'attribute_decl')]

    # 5. Consts
    consts = [process_const(c) for c in get_items_of_type(i, 'const_dcl')]

    return Interface(
        name=name,
        inherits=inherits,
        operations=operations if operations else None,
        attributes=attributes if attributes else None,
        consts=consts if consts else None,
    )


def process_module(m):
    """Process a module_decl rule → Module (recursive).

    Grammar rule:  module_decl: "module" IDENT "{" definition* "}" ";"
    """
    assert_rule_match(m, 'module_decl')

    name_token = m.children.pop(0)
    assert_token(name_token, 'IDENT')
    name = name_token.value

    interfaces  = [process_interface(x)  for x in get_items_of_type(m, 'interface_decl')]
    structs     = [process_struct(x)     for x in get_items_of_type(m, 'struct_decl')]
    enums       = [process_enum(x)       for x in get_items_of_type(m, 'enum_decl')]
    exceptions  = [process_exception(x)  for x in get_items_of_type(m, 'exception_decl')]
    typedefs    = [process_typedef(x)    for x in get_items_of_type(m, 'typedef_decl')]
    consts      = [process_const(x)      for x in get_items_of_type(m, 'const_dcl')]
    submodules  = [process_module(x)     for x in get_items_of_type(m, 'module_decl')]

    return Module(
        name=name,
        interfaces=interfaces   if interfaces   else None,
        structs=structs         if structs       else None,
        enums=enums             if enums         else None,
        exceptions=exceptions   if exceptions    else None,
        typedefs=typedefs       if typedefs      else None,
        consts=consts           if consts        else None,
        modules=submodules      if submodules    else None,
    )


# ============================================================
# Top-level tree processor
# ============================================================

def process_lark_tree(root):
    """Walk the root lark.Tree and build an IDLFile AST.

    Grammar rule:  idl_file: definition*
    """
    assert_rule_match(root, 'idl_file')

    modules    = [process_module(x)    for x in get_items_of_type(root, 'module_decl')]
    interfaces = [process_interface(x) for x in get_items_of_type(root, 'interface_decl')]
    structs    = [process_struct(x)    for x in get_items_of_type(root, 'struct_decl')]
    enums      = [process_enum(x)      for x in get_items_of_type(root, 'enum_decl')]
    exceptions = [process_exception(x) for x in get_items_of_type(root, 'exception_decl')]
    typedefs   = [process_typedef(x)   for x in get_items_of_type(root, 'typedef_decl')]
    consts     = [process_const(x)     for x in get_items_of_type(root, 'const_dcl')]

    return IDLFile(
        modules=modules       if modules    else None,
        interfaces=interfaces if interfaces else None,
        structs=structs       if structs    else None,
        enums=enums           if enums      else None,
        exceptions=exceptions if exceptions else None,
        typedefs=typedefs     if typedefs   else None,
        consts=consts         if consts     else None,
    )


# ============================================================
# Grammar loading and parsing
# ============================================================

def _load_grammar() -> str:
    grammar_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'omgidl.grammar')
    with open(grammar_file, 'r') as f:
        return f.read()


def parse_text(text: str) -> IDLFile:
    """Parse OMG IDL source text and return an IDLFile AST."""
    grammar = _load_grammar()
    parser = Lark(grammar, parser='lalr')
    clean = preprocess(text)
    tree = parser.parse(clean)
    return process_lark_tree(tree)


# ============================================================
# Public entry points
# ============================================================

def get_ast_from_idl_file(idl_file: str) -> IDLFile:
    """Read a .idl file and return its IDLFile AST.

    :param idl_file: path to a .idl source file
    :return: IDLFile abstract syntax tree
    """
    with open(idl_file, 'r') as f:
        text = f.read()
    return parse_text(text)


def get_ast_from_idl_text(text: str) -> IDLFile:
    """Parse OMG IDL source text and return an IDLFile AST."""
    return parse_text(text)


# ============================================================
# Script entry point
# ============================================================

if __name__ == '__main__':
    ast = get_ast_from_idl_file(sys.argv[1])
    print(ast_as_yaml(ast))
