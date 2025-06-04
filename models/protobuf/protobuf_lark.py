# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project

from lark import Lark, logger, Tree, Token
from models import protobuf as protobuf_model
from models.common.type_checking_constructor_mixin import add_constructors_to_ast_model
from models.protobuf.protobuf_ast import Option, FieldOption, EnumField, Enumeration, Field, Import, Message, RPC, Service, Proto, StructuredOption
import lark
import os
import re
import sys

# Design Note: The word "tree" here often refers to the lark.Tree() type which
# is part of the tokenized output from the Lark parser - it is in other words
# not yet the Abstract Syntax Tree (AST) we are aiming to build.  It feels more
# like a low-level sequence of tokens, but it has _some_ hierarchical
# structure.

# In this file we build a more understandable and usable data structure.
# The AST we want follows the definitions provided in protobuf_ast.py

# NOTE: The following features are not converted to AST.  They should be
# accepted by the lexer, but the parser then ignores them.
# - OneOf
# - Reserved
# - edition

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
add_constructors_to_ast_model(protobuf_model)

# Remove lines matching regexp
def filter_out(s, re):
    return '\n'.join([l for l in s.split('\n') if not re.match(l)])

# Remove partial lines matching regexp
def filter_out_partial(s, pattern):
    return '\n'.join([re.sub(pattern, "", l) for l in s.split('\n')])

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

# Check if the node is a tree representing a RULE of type "grammar_rule_name"
def rule_match(tree, grammar_rule_name):
    return matcher(tree, Tree(Token('RULE', grammar_rule_name), ['*']))

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

# Assert that node is a Token of *at least one* of the named types
def assert_token_any(node, token_types, data_match='*'):
    if not any(matcher(node, Token(y, "*")) for y in token_types):
        node_string = truncate_string(f"{node!r}")
        raise Exception(f"PROBLEM: Failed expected token type(s):\n        - wanted one of {token_types}\n        - item is: {node_string}")

def is_literal_type(node):
    return (is_token(node) and
            node.type in ['INT', 'FLOATLIT', 'DECIMALLIT', 'OCTALLIT', 'HEXLIT', 'BOOLLIT', 'X_CHARSTRING', 'IDENT'])

# Assert that node is one of the known literal types
def assert_is_literal_type(node):
    if not is_literal_type(node):
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
    rpc_options = get_items_of_type(r, 'option')

    options = []
    for o in rpc_options:
        assert_rule_match(o, 'option')
        od = o.children.pop(0)
        assert_rule_match(od, 'optiondef')
        options.append(process_option(od))

    # === Create RPC object in AST, and add to list ===
    return RPC(name = rpc_name,
               input = input_param,
               returns = return_param,
               #options = None if options == [] else options,
               options = options,
               input_stream = input_stream,
               return_stream = return_stream)

# NOTE: Options at top level and for fields and enums etc, are now unified
# This function expects the actual optiondef part.
def process_option(o):

    # Sanity check
    assert_rule_match(o, 'optiondef')

    # 1. Option Name
    next_node = o.children.pop(0)
    assert_token_any(next_node, ['OPTIONNAME', 'FULLIDENT'])
    option_name = next_node.value.replace('(','').replace(')','')

    # 2. Option Value

    # Here is a weird special case where a keyval mapping can be empty.  E.g. [some_option = {}]
    # The grammar currently set up so that it produces no tokens at all for the
    # keyvalmappings, so we only notice it by having an empty token stream for the option value:
    if len(o.children) >= 1:
        next_node = o.children.pop(0)
    else:
        # It must be a structured option (keyvalmappings) with no values provided
        return Option(option_name, value=None, structuredoptions=[])

    assert_rule_match_any(next_node, ['constant', 'keyvalmappings'])
    rule = next_node.data
    if rule.value == 'constant':
        value_node = next_node.children.pop(0)
        assert_is_literal_type(value_node)
        return Option(option_name, value=value_node.value, structuredoptions=None)
 
    # Structureconstant aka keyvalmappings
    else:
        assert_rule_match(next_node, 'keyvalmappings')
        keyvals = []
        for m in next_node.children:
            assert_rule_match(m, 'keyvalmapping')
            mappings = m.children
            if rule_match(mappings[0], 'nested_enum'):
                pass # FIXME Not implemented for now
                # Nothing appended to keyvals
            else:
                assert(len(mappings) == 2)  # key, and value
                assert_token(m.children[0], 'IDENT') # Name (key) is always an IDENT
                # ... but the value m.children[1] can be IDENT or constant of various types.  Not checked for now
                key = m.children.pop(0).value
                value_rule = m.children.pop(0)
                assert_rule_match(value_rule, 'constant')
                rule = value_rule.data
                if rule.value == 'constant':
                    value_node = value_rule.children.pop(0)
                    if rule_match(value_node, 'arrayconstant'):
                        for a in value_node.children:
                            assert_rule_match(a, 'constant') # Presumably this should be recursive, but for now, no further nesting of arrays supported
                            value_node = a.children.pop(0)  # This is now an IDENT, or a charstring or some other constant
                            value = value_node.value
                    else:
                        pass # value_node is already an end token
                else: 
                    error_message = f"Expected simple constant assigned to key-value mapping, while processing option (nested key-value mappings unsupported!) option node: {o=}, contains unexpected {value_node=}"
                    raise Exception(error_message)

                keyvals.append(StructuredOption(key, value=value_node.value))

        return Option(option_name, value=None, structuredoptions=keyvals)

    return Option(option_name, value=constant_value)

# TODO enumoption should possibly also be handled this way

def process_field_option(o):

    # Sanity check
    assert_rule_match_any(o, ['valueoption'])

    # 1. Option Name
    next_node = o.children.pop(0)
    assert_token(next_node, 'OPTIONNAME')
    # ... remove parens from name - should we do that here, or in later processing?
    option_name = next_node.value.replace('(','').replace(')','')

    # 2. Option Value
    next_node = o.children.pop(0)
    # ... constant rule is inlined, so not a composite node.
    if is_literal_type(next_node):
       option_value = next_node.value
       return FieldOption(name=option_name, value=option_value, structuredoptions=None)
    else:
       # Is a structured constant which is inlined, so we find a keyvalmappings
       assert_rule_match(next_node, 'keyvalmappings')

       keyvals = []
       for m in next_node.children:
           assert_rule_match(m, 'keyvalmapping')
           assert(len(m.children) == 2)  # key, and value
           assert_token(m.children[0], 'IDENT') # Name (key) is always an IDENT
           # ... but the value m.children[1] can be IDENT or constant of various types.  Not checked for now
           key = m.children[0].value
           value = m.children[1].value
           #assert_is_literal_type(value)
           keyvals.append(StructuredOption(key, value=value))
           # Type of the keyval in AST is a 2-tuple

       # FIXME - check if we can just use Option type for all options, including field option
       return FieldOption(name=option_name, value=None, structuredoptions=keyvals)

# MapField is (no longer) a special type in the AST.  Instead it is a field
# with datatype = "map<A,B>".  However, from the lexer/parser point of view it
# is noticed as a separate token stream so we may as well process it in a
# unique function here.
def process_map_field(f):

    # Sanity check
    assert_rule_match(f, 'mapfield')

    next_node = f.children.pop(0)

    # --- 2 key type ---
    assert_token(next_node, 'X_BUILTINTYPE')
    keytype = next_node.value

    # --- 3 value type ---
    next_node = f.children.pop(0)
    if next_node.type in ['X_BUILTINTYPE', 'IDENT']:
        valuetype = next_node.value
    else:
        raise Exception(f'process_map_field: Unexpected node type when interpreting field {next_node=}')

    # --- 4 field name
    next_node = f.children.pop(0)
    assert_token(next_node, 'IDENT')
    fieldname = next_node.value

    # --- 5 field number (thrown away, for now)
    f.children.pop(0)

    # --- 5 field options ---
    options = []
    if len(f.children) > 0:
        next_node = f.children.pop(0)
        assert_rule_match(next_node, 'fieldoptions')
        for o in next_node.children:
            #options.append(process_field_option(o))
            options.append(process_option(o))

    # NOTE: The field number follows next, but is discarded until
    # we find a reason to keep it - see comments in design document.
    return Field(name = fieldname,
                 datatype = "map<" + keytype + "," + valuetype + ">",
                 options = options)


def process_field(f):

    details=""

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
    if next_node.type in ['X_BUILTINTYPE', 'IDENT']:
        fieldtype = next_node.value
    else:
        raise Exception(f'Unexpected node type when interpreting field {details=}\nnode was: {next_node=}')

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
            #options.append(process_field_option(o))
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

    # --- 4. Options? ---
    service_options = get_items_of_type(s, 'option')

    ast_service_options = []
    for o in service_options:
        assert_rule_match(o, 'option')
        od = o.children.pop(0)
        assert_rule_match(od, 'optiondef')
        ast_service_options.append(process_option(od))

    # === Create Service object in AST, and add to list ===
    return Service(name = name,
                   rpcs = ast_rpcs,
                   options = ast_service_options)

def process_message(m):

    details=""

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

    # --- 2.2. Map Fields (list) ---
    fields = get_items_of_type(next_node, 'mapfield')
    ast_mfields = []
    for f in fields:
        ast_mfields.append(process_map_field(f))

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
            options_node = f.children.pop(0)
            assert_rule_match(options_node, 'fieldoptions')
            for o in options_node.children:
                assert_rule_match(o, 'optiondef')
                ast_enum_value_options.append(process_option(o))

        ast_fields.append(EnumField(name = field_name,
                                    value = value,
                                    #options = None if ast_enum_value_options == [] else ast_enum_value_options))
                                    # FIXME - type checking constructor does not allow assigning None
                                    options = ast_enum_value_options))

    # 2. Options (on the enum itself, not the enum value)
    options = get_items_of_type(next_node, 'option')
    ast_options = []
    for o in options:
        # Node of option type -> process the embedded optiondef
        # Should be one child of type optiondef here
        assert(len(o.children) == 1)
        optiondef_node = o.children.pop(0)
        assert_rule_match(optiondef_node, 'optiondef')
        ast_options.append(process_option(optiondef_node))

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
        # Node of option type -> process the embedded optiondef
        # Should be one child of type optiondef here
        assert(len(o.children) == 1)
        optiondef_node = o.children.pop(0)
        assert_rule_match(optiondef_node, 'optiondef')
        ast_options.append(process_option(optiondef_node))

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

def read_proto_file(proto_file) -> str:
    with open(proto_file, 'r') as f:
        proto = f.read()

        # Remove comment-lines
        proto = filter_out(proto, re.compile('^ *[/][/]'))

        # Remove comments at end of line
        proto = filter_out_partial(proto, r'//.*$')

        # Remove multi-line comments
        return re.sub(r"/\*.*?\*/", "", proto, flags=re.DOTALL)


def parse_proto_file(grammar_file, proto_file):
    """
    Tries to parse proto/grpc into a python dictionary
    :param string: String containing text in .proto format
    :return: Dictionary
    """

    with open(grammar_file, 'r') as f:
        grammar = f.read()

        proto = read_proto_file(proto_file)

        p = Lark(grammar, parser='lalr', debug=True)

        # Get parsed content
        tree = p.parse(proto)
        return process_lark_tree(tree)

def parse_text(text):

    # Get location of protobuf model - in the same place we find the grammar
    modeldir=os.path.dirname(protobuf_model.__file__)
    grammar_file = os.path.join(modeldir, 'protobuf.grammar')

    with open(grammar_file, 'r') as f:
        grammar = f.read()

        p = Lark(grammar, parser='lalr', debug=True)

        # Get parsed content
        tree = p.parse(text)
        return process_lark_tree(tree)


# Convenience function - grammar file can be derived from parser module directory
def get_ast_from_proto_file(protofile: str) -> Proto:
    """
    Reads a .proto file and returns Protobuf AST
    :param filename: path to a .proto file
    :return: Protobuf/gRPC abstract syntax tree
    """

    # Get location of protobuf model - in the same place we find the grammar
    modeldir=os.path.dirname(protobuf_model.__file__)
    grammar_file = os.path.join(modeldir, 'protobuf.grammar')
    return parse_proto_file(grammar_file, protofile)


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

    ast = get_ast_from_proto_file(proto_file = sys.argv[1])
    print(ast)
