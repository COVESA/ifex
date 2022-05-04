# SPDX-License-Identifier: MPL-2.0
# ----------------------------------------------------------------------------
# (C) 2021 COVESA
# Reader/parser module
# To be used by all generators and other tools
# ----------------------------------------------------------------------------

"""
VSC parser/reader to be used by generators and other tools
"""

# This performs the following related functions:

# 1. Read a service description file from its YAML format into it simple
#    representation of dicts and lists.  This model the structure of the YAML
#    file, but contains basically the plain text items therein with no more
#    elaborate type information.  It is done using the standard 'yaml'
#    library of python.
#
# 2. Go through the tree and create a linked tree of Nodes (instances of
#    typed classes).  Each node gets a more specific type than
#    dict/list/string which can be used to evaluate the tree contents later.
#    In most parsers, this is referred to an Abstract Syntax Tree (AST)
#    representation of the program.
#    The nodes are also inheriting functionality from the base Node type of
#    the anytree library, which means convenience functions from anytree
#    can be used to manipulate the tree later.
#
# 3. Indirectly, when building the AST, it is done with knowledge about
#    which node types are expected and belong there, and so it can check
#    and report if certain conditions are not met.  It does not check all
#    possible rules however, and would be well complimented by a schema
#    checker.
from __future__ import annotations
import yaml
import anytree

# ----------------------------------------------------------------------------
# VSC Abstract Syntax Tree
# ----------------------------------------------------------------------------
# This following list of classes and the schema definition that follows,
# shows the service file format hierarchy in quite readable form by the
# help of the type hints for each member, although it in itself does not
# explain all possible rules and constraints.
#
# Each AST object also derives from anytree.Node to be able to use the
# convenience functions of the anytree library.

# Base class for all nodes in the tree
class AST(anytree.Node):
    def __init__(self, name, parent):
        super().__init__(name, parent)

# AST node types.  They are all subtypes of the AST node.  They are empty
# because the member variables are later added at run-time, as defined by
# the schema variable.
class Argument(AST): pass
class Enum(AST): pass
class Error(AST): pass
class Event(AST):  pass
class Include(AST): pass
class Member(AST): pass
class Method(AST): pass
class Namespace(AST): pass
class Option(AST): pass
class Property(AST): pass
class Service(AST): pass
class Struct(AST): pass
class Typedef(AST): pass

# Some identifiers used to indicate optionality
MAN = 0 # MAN(datory)
REC = 1 # REC(ommended)
OPT = 2 # OPT(ional)

schema = {
    # Root node can theoretically contain several services
    # ... one Service = one file, presumably.
    "AST" : {
        "services" : (list[Service], MAN)
        },

    "Argument" : {
        "name" : (str, MAN),
        "description" : (str, REC),
        "datatype" : (str, MAN),
        "arraysize" : (str, OPT),
        "range"  : (str, OPT)
        },

    "Error" : {
        "datatype" : (str, MAN),
        "arraysize" : (str, OPT),
        "range" : (str, OPT)
        },

    "Method" : {
        "name" : (str, MAN),
        "description" : (str, MAN),
        "in" : (list[Argument], OPT),
        "out" : (list[Argument], OPT),
        "errors" : (Error, REC)
        },

    "Event" : {
        "name" : (str, MAN),
        "description" : (str, REC),
        "in" : (list[Argument], OPT)
        },

    "Property" : {
        "name" : (str, MAN),
        "description" : (str, REC),
        "datatype" : (str, MAN),
        "arraysize" : (str, OPT)
        },

    "Member" : {
        "name" : (str, MAN),
        "description" : (str, REC),
        "datatype" : (str, MAN),
        "arraysize" : (str, OPT)
        },

    "Option" : {
        "name" : (str, MAN),
        "value" : (str, MAN),
        "description" : (str, REC)
        },

    "Struct" : {
        "name" : (str, MAN),
        "description" : (str, REC),
        "members" : (list[Member], MAN)
        },

    "Typedef" : {
        "name" : (str, MAN),
        "description" : (str, REC),
        "datatype" : (str, MAN),
        "arraysize" : (str, OPT),
        "min" : (str, OPT),
        "max" : (str, OPT)
        },

    "Enum" : {
        "name" : (str, MAN),
        "datatype" : (str, MAN),
        "description" : (str, REC),
        "options" : (list[Option], MAN)
        },

    "Namespace" : {
        "name" : (str, MAN),
        "description" : (str, REC),
        "major_version" : (str, OPT),
        "minor_version" : (str, OPT),
        "typedefs" : (list[Typedef], OPT),
        "structs" : (list[Struct], OPT),
        "enumerations" : (list[Enum], OPT),
        "methods" : (list[Method], OPT),
        "events" : (list[Event], OPT),
        "properties" : (list[Property], OPT),
        "includes" : (list[Include], OPT)
        },

    "Include" : {
        "file" : (str, MAN),
        "description" : (str, REC)
        },

    "Service" : {
        "name" : (str, MAN),
        # TODO major/minor-version
        "major_version" : (str, REC),
        "minor_version" : (str, REC),
        "description" : (str, REC),
        "namespaces" : (list[Namespace], MAN)
        }
}

# ----------------------------------------------------------------------------
# YAML reading
# ----------------------------------------------------------------------------

# Exceptions and debug
class YAMLMissingNode(BaseException):
    def __init__(self, msg):
        self.msg = msg

def debug(msg):
    # TODO something better?
    dummy = 1

# YAML reader
def read_yaml_to_dict(filepath):
    with open(filepath, "r") as f:
        tree = yaml.load(f.read(), Loader=yaml.SafeLoader)
        if tree:
            return tree

    # If failed, replace None with an empty dict
    return {}

# Helper which throws an exception and error message if an expected node is
# missing in the YAML tree
def get_yaml_value(tree, nodename, allow_none=False):
    node = tree.get(nodename)
    if node is None:
        if allow_none:
            return None
        else:
            raise YAMLMissingNode(f'ERROR: Missing expected node named "{nodename}" in YAML definition')

    # whitespace at start or end makes no sense, so remove it.
    if type(node) is str:
        node = node.strip()
    return node

# Helper which returns None if an optional node is missing in the YAML tree
def get_optional_yaml_value(tree, nodename):
    node = tree.get(nodename)
    if node is None:
        # FIXME: Give more context information to the user (e.g. line # number)
        debug(f'INFO:Not found (optional) value of type "{nodename}"')
    if type(node) is str:
        node = node.strip()
    return node

# Helper which WARNS if node not found in YAML tree
def get_recommended_yaml_value(tree, nodename):
    node = tree.get(nodename)
    if node is None:
        # FIXME: Give more context information to the user (e.g. line # number)
        print(f'WARNING: Recommended value of type "{nodename}: was not found"')
    if type(node) is str:
        node = node.strip()
    return node

# ----------------------------------------------------------------------------
# AST Node constructors
# ----------------------------------------------------------------------------

# Here we construct a graph of nodes using typed classes (AST
# subclasses) that are also AnyTree Nodes, from an input tree that
# represents the raw YAML text but read into a tree in the standard
# dict/list format from the YAML parser.

# ERROR/WARNINGS/INFO provided if the structure is not as expected but it
# primarily is able to tell what is missing, and does not do well in
# recognizing any _additional_ and unexpected data in the YAML definition.
# Some additional constraints might be placed in this part of the code.
# But schema-validation should be applied in addition to catch also
# unintended nodes better than this code.

# Input parameters to each:
# - parent = AST object, parent object of the nodes to be constructed
# - yamltree = YAML sub-tree, represented as a Dict/List.  (The standard
#   representation coming out of the standard python yaml module)

class ASTNodeError(BaseException):
    def __init__(msg):
        self.msg = "msg"

# Helper to check if a returned YAML snippet is a list, or throw assertion
def ensure_it_is_yaml_list(yaml, parent_name : str):
    # Empty check should have been done before, but for good measure:
    assert (yaml != None), f'BUG: Found empty/None node near/below {parent_name} in YAML definition'

    if not isinstance(yaml, list):
        ASTNodeError(f"Expected a list of command objects under {parent_name}, not just a single. If there is only one, specify a list, but with one object only")

def ast_Node(parent, nodetype, yamltree):
    node_members = schema[nodetype]
    # Get name so we can pass it to the node constructor
    # (Node names make up the "path" in the AnyTree node concept)
    name = get_yaml_value(yamltree, 'name', allow_none=True)
    if name is None:
        print("WARNING: Node name for {node} was not defined -> using None!")
    # The following line gets a reference to the AST subclass that is named "name".
    class_ = eval(nodetype)
    # And this creates an instance of that class, i.e. an AST node.
    node = class_(name, parent)
    #    print(f"Parser: Created node {node}")

    # In the schema we have a dict that maps member names to their # type/content
    # We destructure this into its parts
    for (membername, (type, optionality)) in node_members.items():
        node.__setattr__(membername, get_node_member(node, type, optionality, membername, yamltree))
    return node

# Build the AST from the parsed YAML starting at the root.
def ast_Root(yamltree):

    # Empty root node at the top.
    root = AST("ast", None)

    try:
        # Extend here if more than one service is going to be processed at
        # the same time.  For now, we set a vector of services containing
        # only one item.
        root.services = [ast_Node(root, 'Service', yamltree)]

    except ASTNodeError:
        print("AST Node Exception, FIXME")

    return root

def get_subtree(yamltree, keyname, optionality):
    match optionality:
        case 0:
            return get_yaml_value(yamltree, keyname)
        case 1:
            return get_recommended_yaml_value(yamltree, keyname)
        case 2:
            return get_optional_yaml_value(yamltree, keyname)

def get_node_member(parent, t, optionality, membername, yamltree):
#    print(f"get_node_member for type {t} = {t.__name__}")
#    print(f"t.__name__ is {t.__name__}")
    match t.__name__:
        case "list":
            # Determine name of the AST Node type class contained in list
            # (such as "Namespace", "Member", "Argument", "Error" etc.)
            contained_type = t.__args__[0]
            contained_type_name = t.__args__[0].__name__

            # Search for subtree in YAML and complain if anything
            # non-optional is missing.
            subtree = get_subtree(yamltree, membername, optionality)
            if subtree is None: # (For example optional item)
                return []

            ensure_it_is_yaml_list(subtree, membername)

            nodes = []
            for items in subtree:
                # recurse
                nodes.append(ast_Node(parent, contained_type_name, items))
            return nodes
        case "str":
            return get_subtree(yamltree, membername, optionality)
        case _: # All other cases assumed to be a single AST node class (not list of nodes)
            return get_subtree(yamltree, membername, optionality)

def get_ast_from_file(filepath : str):
    return ast_Root(read_yaml_to_dict(filepath))

def print_ast(ast : AST):
    print(anytree.RenderTree(ast))

# Test code
#d = read_yaml_to_dict('seats-service.yml')
#a = get_AST_from_file('seats-service.yml')
#print_ast(a)
#x = a
#r = anytree.Resolver()
#x = r.get(a, "//")

