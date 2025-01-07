# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project

from lark import Lark, logger, Tree, Token
from models.protobuf.protobuf_ast import Option, EnumField, Enumeration, MapField, Field, Import, Message, RPC, Service, Proto
import lark
import re
import sys

# Design Note: The word "tree" here often refers to the lark.Tree() type which
# is part of the tokenized output from the Lark parser - it is in other words
# not yet the Abstract Syntax Tree (AST) we are aiming to build.  It feels more
# like a low-level sequence of tokens, but it has _some_ hierarchical
# structure.

# In this file we build a more understandable and usable data structure.
# The AST we want follows the definitions provided in protobuf_ast.py

# NOTE: The following features are not converted to AST:
# - OneOf
# - Reserved

# The datastructure we get out of Lark is a combination of Tree and Token
# objects.  This is how to understand it -- we are only interested in two
# member-variables for each object type, as follows:
#
# Tree(data, children):
#    .data   always holds: Token('RULE', 'something') where 'something' is the name
#            of the rule in the grammar.  The type of that token is always = 'RULE'.
#    .children = a python list of additional Tree or Token objects
#
# Token(type, value):
#    .type =  The NAME of the literal defined in the grammar (literals are
#             defined by simple regexp expressions, and the name is in capital
#             letters)
#    .value = The string value that matched the regexp


# Use protobuf_construction mixin
import models.protobuf.protobuf_ast_construction as protobuf_ast_construction
protobuf_ast_construction.add_constructors_to_protobuf_ast_model()

# Remove lines matching regexp
def filter_out(s, re):
    return '\n'.join([l for l in s.split('\n') if not re.match(l)])

# Useful helpers
def is_tree(node):
    return type(node) is lark.Tree

def is_token(node):
    return type(node) is lark.Token

def truncate_string(s, maxlen=77):
    if len(s) > maxlen:
        return s[0:maxlen] + "..."
    else:
        return s

# PATTERN MATCHING
#
# Here we build a set of functions that will take a pattern token-tree
# and compare it to the real token tree, to be able to recognize and extract
# features more easily.  For both the Tree and Token type, it is possible to
# specify the .children or .value to match against, or to pass a wildcard.
# (we use ['*'] for lists (children) and '*' for strings (value) to match
# any value therein.

# String matcher which allows "*" = wildcard on the string we are comparing *to*!
def match_str(s1,s2):
    return s1 == s2 or s2 == "*"

# Checks that all objects in node-list match the corresponding pattern-list
def match_children(node_list, pattern_list):
    # Wildcard ['*'] matches any list
    return (pattern_list == ['*'] or
        # If not wildcard, the whole list must be equal:
        (len(node_list) == len(pattern_list) and
         all(matcher(x,y) for (x,y) in zip(node_list, pattern_list))))

# Match any node against a pattern - can use wildcard in the treepattern
# For Tree nodes, it will recurse and require the entire sub-tree to match.
def matcher(node, pattern):

    # Loop (recurse) over lists
    if type(node) is list:
        return ( pattern is list and
                 len(node) == len(pattern) and
                 all(matcher(x,y) for (x,y) in zip(node, pattern)) )

    # Loop (recurse) over trees
    elif is_tree(node):
        return ( is_tree(pattern) and
                node.data == pattern.data and
                match_children(node.children, pattern.children))

    # Plain node - do wildcard match of type and content
    elif is_token(node):
        return ( is_token(pattern) and
                match_str(node.type, pattern.type) and
                match_str(node.value, pattern.value) )
    # => ?
    else:
        raise TypeException("Unknown type passed to matcher() - please check!")


# Helper to extract a subtree of a certain type (as identified by the grammar rule name)
def get_items_of_type(node, grammar_rule_name):
    return [x for x in node.children if matcher(x, Tree(Token('RULE', grammar_rule_name), ['*'])) ]


# ASSERTS - Functions to check that we have the expected format of the token-tree
# (Lark parser output).
#
# If we get invalid input then the parsing should _usually_ fail earlier
# according to the grammar rules.  In the rest of the program we should have
# the right understanding of which sequence of tokens is received but asserts
# are used to check this understanding.  If there is a mistake, these assert
# calls can help to catch it instead of passing invalid data to the next step.
#
# During development and later it is i.o.w. possible that these will throw
# exception once in a while, to notify that something needs to be adjusted.

def create_error_message(node, pattern):
       node_string = truncate_string(f"{node!r}")
       pattern_string = truncate_string(f"{pattern!r}")
       return f"\nPROBLEM: Failed expected match:\n         - wanted pattern: {pattern_string}\n         - item is: {node_string}"

# Raise exception if a node does not matches a pattern
def assert_match(node, pattern, error_message=None):
    if not matcher(node, pattern):
       # Create a useful error message, if not specified:
       if error_message is None:
           error_message = create_error_message(node, pattern)
       raise Exception(error_message)

# Assert that the node is a tree representing a RULE of type "grammar_rule_name"
def assert_rule_match(tree, grammar_rule_name):
   assert_match(tree, Tree(Token('RULE', grammar_rule_name), ['*']))

# Assert that tree matches *at least one* of the named rules
def assert_rule_match_any(tree, grammar_rule_names):
    if not any(matcher(tree,Tree(Token('RULE',y), ['*'])) for y in grammar_rule_names):
        node_string = truncate_string(f"{tree!r}")
        raise Exception(f"PROBLEM: Failed expected match:\n        - wanted one of {grammar_rule_names}\n        - item is: {node_string}")

# Assert that node is a Token of the given type, optionally checking
# for specific data (or wildcard)
def assert_token(node, token_type, data_match='*'):
    assert_match(node, Token(token_type, data_match))

# Assert that node is one of the known literal types
def assert_is_literal_type(node):
    if not (is_token(node) and
            node.type in ['INT', 'FLOATLIT', 'DECIMALLIT', 'OCTALLIT', 'HEXLIT', 'BOOLLIT', 'X_CHARSTRING', 'IDENT']):
        node_string = truncate_string(f"{node!r}")
        error_message = f"\nPROBLEM: Failed expected match:\n          - wanted a INT, FLOATLIT, DECIMALLIT, OCTALLIT, HEXLIT, BOOLLIT, or X_CHARSTRING\n          - item is: {node_string}"
        raise Exception(error_message)


# --- MAIN PROCESSING FUNCTIONS ---

def process_rpc(r):

    # Sanity check
    assert_rule_match(r, 'rpc')

    # --- 1. RPC Name ---
    rpc_node = r.children.pop(0)
    assert_token(rpc_node, 'IDENT')
    rpc_name = rpc_node.value

    # --- 2. Input message type ---
    next_node = r.children.pop(0)

    # Catch stream keyword, if it's there
    input_stream = False
    if matcher(next_node, Token('X_STREAM', '*')):
        input_stream = True
        next_node = r.children.pop(0)

    assert_token(next_node, 'MESSAGETYPE')
    input_param = next_node.value

    # --- 3. Return value ---
    next_node = r.children.pop(0)

    # Catch stream keyword, if it's there
    return_stream = False
    if matcher(next_node, Token('X_STREAM', '*')):
        return_stream = True
        next_node = r.children.pop(0)

    assert_token(next_node, 'MESSAGETYPE')
    return_param = next_node.value

    # --- 4. Options? ---

    options = []
    if len(r.children) > 0:
        option_node = r.children.pop(0)
        options.append(process_option(option_node))

    # === Create RPC object in AST, and add to list ===
    return RPC(name = rpc_name,
               input = input_param,
               returns = return_param,
               #options = None if options == [] else options,
               options = options,
               input_stream = input_stream,
               return_stream = return_stream)

# NOTE: As of now the grammar uses two different types of option definitions
# (option and valueoption) so the node test at the beginning is accordingly,
# but the rest of the token stream is identical and the meaning of options is
# the same, or extremely similar, so this function processes all options, for
# any type of object into an Option AST node.
def process_option(o):

    # Sanity check
    assert_rule_match_any(o, ['option', 'valueoption', 'enumoption'])

    # 1. Option Name
    next_node = o.children.pop(0)
    assert_token(next_node, 'OPTIONNAME')
    # ... remove parens from name - should we do that here, or in later processing?
    option_name = next_node.value.replace('(','').replace(')','')

    # 2. Option Value
    next_node = o.children.pop(0)
    # ... constant rule is inlined, so not a composite node.
    assert_is_literal_type(next_node)
    constant_value = next_node.value

    return Option(option_name, constant_value)


def process_field(f):

    # Sanity check
    assert_rule_match(f, 'field')

    # --- 1 repeated? ---
    next_node = f.children.pop(0)
    repeated = False
    if next_node.type == 'X_REPEATED':
        repeated = True
        next_node = f.children.pop(0) # Skip to next token

    # --- 1.1 optional ---
    optional = False
    if next_node.type == 'X_OPTIONAL':
        optional = True
        next_node = f.children.pop(0) # Skip to next token

    # --- 2 field type ---
    if next_node.type in ['X_BUILTINTYPE', 'DEFINEDTYPE']:
        fieldtype = next_node.value
    else:
        raise Exception(f'Unexpected node type when interpreting field {details=}')

    # --- 3 field name ---
    next_node = f.children.pop(0)
    assert_token(next_node, 'IDENT')
    fieldname = next_node.value

    # --- 4 field number (thrown away, for now)
    f.children.pop(0)

    # --- 5 field options ---
    options = []
    if len(f.children) > 0:
        next_node = f.children.pop(0)
        assert_rule_match( next_node, 'fieldoptions')
        for o in next_node.children:
            options.append(process_option(o))

    # NOTE: The field number follows next, but is discarded until
    # we find a reason to keep it - see comments in design document.
    return Field(name = fieldname,
                 datatype = fieldtype,
                 repeated = repeated,
                 optional = optional,
                 options = options)

def process_service(s):

    # Sanity check
    assert_rule_match(s, 'service')

    # 1. Name
    name_node = s.children.pop(0)
    assert_token(name_node, 'IDENT')
    name = name_node.value

    # 2. In-service features: RPC
    rpcs = get_items_of_type(s, 'rpc')
    ast_rpcs = []
    for r in rpcs:
        ast_rpcs.append(process_rpc(r))

    # 3. In-service features: Option
    service_options = get_items_of_type(s, 'option')
    ast_service_options = []
    for o in service_options:
        ast_service_options.append(process_option(o))

    # === Create Service object in AST, and add to list ===
    return Service(name = name,
                   rpcs = ast_rpcs,
                   options = ast_service_options)

def process_message(m):

    # Sanity check
    assert_rule_match(m, 'message')

    # --- 2.1. Message Name ---
    next_node = m.children.pop(0)
    assert_token(next_node, 'IDENT')
    msg_name = next_node.value

    # --- 2.2. Message Fields (list) ---
    next_node = m.children.pop(0)
    assert_rule_match(next_node, 'messagebody')

    fields = get_items_of_type(next_node, 'field')
    ast_fields = []
    for f in fields:
        ast_fields.append(process_field(f))

    # --- 2.3 (Nested) messages
    messages = get_items_of_type(next_node, 'message')
    ast_messages = []
    for m in messages:
        # Recurse to take care of nested message
        ast_messages.append(process_message(m))

    # --- 2.3 (Nested) enums
    enums = get_items_of_type(next_node, 'enum')
    ast_enums = []
    for e in enums:
        # Recurse to take care of nested message
        ast_enums.append(process_enums(e))

    # === Create Message object in AST, and add to list ===
    return Message(name = msg_name,
                   fields = ast_fields,
                   messages = ast_messages,
                   enums = ast_enums)


def process_package(p):

    # Sanity check
    assert_rule_match(p, 'package')

    # Package is in AST represented by a string (the name) only:
    return p.children.pop(0).value


def process_imports(i):

    # Sanity check
    assert_rule_match(i, 'import')

    next_node = i.children.pop(0)

    # 1. Import modifier? (optional)
    weak = public = False
    if next_node.type == 'X_IMPORTMODIFIER':
        if next_node.value == 'weak':
            weak = True
        elif next_node.value == 'public':
            public = True
        else:
            # This is probably impossible due to the grammar rule, but to be certain:
            raise Exception("Unexpected import modifier: {next_node.value} (should be 'weak' or 'public' or none)")

        # Skip to next
        next_node = i.children.pop(0)

    # 2. The path
    assert_token(next_node, 'X_CHARSTRING')
    path = next_node.value

    return Import(path = path,
                  weak = weak,
                  public = public)


def process_enums(e):

    # Sanity check
    assert_rule_match(e, 'enum')

    next_node = e.children.pop(0)
    assert_token(next_node, 'IDENT')
    enum_name = next_node.value

    # Extract Enum body
    next_node = e.children.pop(0)
    assert_rule_match(next_node, 'enumbody')

    # 1. Fields
    fields = get_items_of_type(next_node, 'enumfield')
    ast_fields = []
    for f in fields:

        # 1.1 Enum Field name
        name_node = f.children.pop(0)
        assert_token(name_node, 'IDENT')
        field_name = name_node.value

        # 1.2 Enum Field value
        value_node = f.children.pop(0)
        assert_is_literal_type(value_node)
        value = value_node.value

        # Addititional tokens? -> must be EnumValueOptions
        # 1.3 enum options
        ast_enum_value_options = []
        while len(f.children) > 0:
            option_node = f.children.pop(0)
            ast_enum_value_options.append(process_option(option_node))

        ast_fields.append(EnumField(name = field_name,
                                    value = value,
                                    #options = None if ast_enum_value_options == [] else ast_enum_value_options))
                                    # FIXME - type checking constructor does not allow assigning None
                                    options = ast_enum_value_options))

    # 2. Options (on the enum itself, not the enum value)
    options = get_items_of_type(next_node, 'enumoption')
    ast_options = []
    for o in options:
        ast_options.append(process_option(o))

    # 3. TODO: Reservations

    return Enumeration(name = enum_name,
                       fields = ast_fields,
                       #options = None if ast_options == [] else ast_options,
                       options = ast_options,
                       reservations = [] # FIXME later
                       )


# Top-level root node process
def process_lark_tree(root):

    # Sanity check
    assert_rule_match(root, 'proto')

    # 0. Top-level features: PACKAGE
    packages = get_items_of_type(root, 'package')

    if len(packages) > 1:
        Exception("Multiple package statements found!  The protobuf spec is ambiguous on multiple package statements (EBNF grammar allows multiple but the explanation suggests a singular use).  This implementation chose to support only one per file.  (If multiple are needed, please contact the IFEX project)")
    ast_package = None
    if len(packages) > 0:
        ast_package = process_package(packages[0])

    # 1. Top-level features: IMPORT
    imports = get_items_of_type(root, 'import')
    ast_imports = []
    for i in imports:
        ast_imports.append(process_imports(i))

    # 2. Top-level features: SERVICE
    services = get_items_of_type(root, 'service')
    ast_services = []
    for s in services:
        ast_services.append(process_service(s))

    # 3. Top-level features: MESSAGE
    messages = get_items_of_type(root, 'message')
    ast_messages = []
    for m in messages:
        ast_messages.append(process_message(m))

    # 4. Top-level features: ENUM
    enums = get_items_of_type(root, 'enum')
    ast_enums = []
    for e in enums:
        ast_enums.append(process_enums(e))

    # 5. Top-level features: OPTION
    options = get_items_of_type(root, 'option')
    ast_options = []
    for o in options:
        ast_options.append(process_option(o))

    # 6. Top-level features: SYNTAX -> ignored (always = 'proto3')

    # === Create and return proto tree root node ===

    proto = Proto(package = ast_package,
                imports = ast_imports,
                services = ast_services,
                messages = ast_messages,
                enums = ast_enums,
                options = ast_options)
    return proto


# Main entry point - pass grammar file and proto file:

def create_proto_ast(grammar_file, proto_file):
    with open(grammar_file, 'r') as f:
        grammar = f.read()

    p = Lark(grammar, parser='lalr', debug=True)

    with open(proto_file, 'r') as f:
        proto = f.read()

        # Remove line comments
        proto = filter_out(proto, re.compile('^ *[/][/]'))

        # Remove multi-line comments
        proto = re.sub(r"/\*.*?\*/", "", proto, flags=re.DOTALL)

        # Get parsed content
        tree = p.parse(proto)

        # Return Protobuf AST
        return process_lark_tree(tree)


# TEST CODE ONLY ------------------------------------------
if __name__ == '__main__':

    # Test matcher function
    x = lark.Tree(lark.Token('RULE','foo'),[lark.Token('x','y')])
    print(f"{matcher(x, lark.Tree(lark.Token('RULE','foo'), [lark.Token('x','y')]))=}")

    x = lark.Tree(lark.Token('RULE','foo'),[lark.Token('x','WRONG')])
    print(f"{matcher(x, lark.Tree(lark.Token('RULE','foo'), [lark.Token('x','*')]))=}")

    x = lark.Tree(lark.Token('RULE','foo'),[])
    print(f"{matcher(x, lark.Tree(lark.Token('RULE','foo'), []))=}")

    x = lark.Tree(lark.Token('RULE','something'),[])
    print(f"{matcher(x, lark.Tree(lark.Token('RULE','notmatching'), []))=}")

    ast = create_proto_ast(grammar_file = sys.argv[1],
                           proto_file = sys.argv[2])
    print(ast)
