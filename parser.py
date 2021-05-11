# ----------------------------------------------------------------------------
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
#    dict/list/string which can be used to evalute the tree contents later.
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

import yaml
import anytree

# ----------------------------------------------------------------------------
# VSC Abstract Syntax Tree
# ----------------------------------------------------------------------------
# This following list of classes shows the service file format hierarchy in
# quite readable form by the help of the type hints for each member,
# although it in itself does not explain all possible rules and
# constraints.  For example, optionality can not be seen by looking at the
# class structure alone.
#
# Each AST object also derives from anytree.Node to be able to use the
# convenience functions of the anytree library.
#
# Note: The class list is best read bottom up.  Since a type must be
# defined before it is used, the top level concepts objects will be
# found near the bottom.

# Base class for all nodes in the tree
class AST(anytree.Node):
   def __init__(self, name, parent):
       super().__init__(name, parent)

class Argument(AST):  # for in_arguments and out_arguments
   name: str
   description: str
   type: str

class Command(AST):
   name: str
   description: str
   in_arguments: list[Argument]

class Method(AST):
   name: str
   description: str
   in_arguments: list[Argument]
   out_arguments: list[Argument]

class Event(AST):  # Note: Event details are TBC
   name: str
   description: str
   in_arguments: list[Argument]

class Interface(AST):
   name: str
   description: str
   commands: list[Command]
   methods: list[Method]
   events: list [Event]  # TBC

class Member(AST):
   name: str
   type: str
   description: str

class Option(AST):
   name: str
   value: str

class Type(AST):
   name: str
   type: str
   min: str                 # only makes sense for number types
   max: str                 # ---------- " -----------
   description: str
   enum_type: str           # used only if a enum_type
   options: list[Option]    # ---------- " -----------

   members: list[Member]    # used only if a struct type

class Namespace(AST):
   description: str
   types: list[Type]

# FIXME  This node type might be superfluous since it has only one member?
# All other nodes have more than one member, or the list of [X] is simply
# directly listed in the parent node type.  In this case datatypes always
# are made up of a list of namespaces, so it seems that's an unnecessary
# step?
class Datatypes(AST):
   namespaces: list[Namespace]

class Service(AST):
   name: str
   description: str
   datatypes: Datatypes        # or list[Namespace] see above
   interfaces: list[Interface]

# ----------------------------------------------------------------------------
# YAML reading
# ----------------------------------------------------------------------------

# Exceptions and debug
class YAMLMissingNode(BaseException):
    def __init__(self, msg):
        self.msg = msg

def debug(msg):
    # TODO something better?
    #print(msg)
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
def get_yaml_value(tree, nodename):
    node = tree.get(nodename)
    if node is None:
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

# The following helper functions each construct a AST object.  Each object is a
# node in the abstract syntax tree.  Instead of a single recursive tree
# walker function, these are separately typed functions.  The function call
# flow for adding children for each type is controlled in each, because we know the
# type of nodes to expect under each node.  On the other hand, this means
# reading the code becomes a kind of specification of what the
# allowed/expected children are for each node.

# ERROR/WARNINGS/INFO provided if the structure is not as expected but it
# primarily is able to tell what is missing, and does not do well in
# recognizing any _additional_ and unexpected data in the YAML definition.
# Some additional constraints might be placed in this part of the code.
# But schema-validation should be applied in addition to catch also
# unintended nodes better than this code.

# The naming convention is:  ast_<class-name-for-AST-node-type>()

# For understanding these ast helper functions, study ast_Service() first
# which is well commented.  The others are similar, and written with less
# or without comments.

# Input parameters to each:
# - parent = AST object, parent object of the nodes to be constructed
# - yamltree = YAML sub-tree, represented as a Dict/List.  (The standard
#   representation coming out of the standard python yaml module)

class ASTNodeError(BaseException):
    def __init__(msg):
       self.msg = "msg"

# Helper to check if a returned YAML snippet is a list, or throw assertion
def require_list(yaml, parent_name : str):
    # Empty check should have been done before, but for good measure:
    assert (yaml != None), f'BUG: Found empty/None node near/below {parent_name} in YAML definition'

    if not isinstance(yaml, list):
        ASTNodeError(f"Expected a list of command objects under {parent_name}, not just a single. If there is only one, specify a list, but with one object only")

def ast_Types(parent, yamltree) -> Type:
    subtrees = get_yaml_value(yamltree, 'types')
    require_list(subtrees, 'types')

    nodes = []
    for st in subtrees:
        node = Type(get_yaml_value(st, 'name'), parent)
        node.type = get_yaml_value(st, 'type')
        node.description = get_recommended_yaml_value(st, 'description')

        # Some conditionals might be here.  E.g. only if type integer
        # does it make sense to fetch min/max?
        node.min = get_optional_yaml_value(st, 'min')
        node.max = get_optional_yaml_value(st, 'max')
        nodes.append(node)

    return nodes

def ast_Namespace(parent, yamltree) -> Namespace:
        name = get_yaml_value(yamltree, 'namespace')
        node = Namespace(name, parent)
        node.description = get_yaml_value(yamltree, 'description')
        node.types = ast_Types(node, yamltree)
        return node

def ast_Datatypes(parent, yamltree) -> Datatypes:
        subtrees = get_yaml_value(yamltree, 'datatypes')
        require_list(subtrees, 'datatypes')

        nodes = []
        for st in subtrees:
            # There is no name for this type of node, so just use 'datatypes'
            node = Datatypes('datatypes', parent)
            node.namespaces = ast_Namespace(node, st)
            nodes.append(node)

        return nodes

def ast_Arguments(parent, yamltree, argtype = 'in_arguments') -> list[Argument]:
    subtrees = get_yaml_value(yamltree, argtype)
    require_list(subtrees, f'{argtype}')

    nodes = []
    for st in subtrees:
        node = Argument(get_yaml_value(st, 'name'), parent)
        node.description = get_yaml_value(st, 'description')
        node.type = get_yaml_value(st, 'type')
        nodes.append(node)

    return nodes

def ast_Commands(parent, yamltree) -> list[Command]:
    subtrees = get_optional_yaml_value(yamltree, 'commands')

    # (Optional)
    if subtrees is None:
       return None
    require_list(subtrees, 'commands')

    nodes = []
    for st in subtrees:
        node = Command(get_yaml_value(st, 'name'), parent)
        node.description = get_yaml_value(st, 'description')
        node.in_arguments = ast_Arguments(node, st)
        nodes.append(node)

    return nodes

def ast_Methods(parent, yamltree) -> list[Method]:
    subtrees = get_optional_yaml_value(yamltree, 'methods')

    # (Optional)
    if subtrees is None:
       return []
    require_list(subtrees, 'methods')

    nodes = []
    for st in subtrees:
        node = Command(get_yaml_value(st, 'name'), parent)
        node.description = get_yaml_value(st, 'description')
        node.in_arguments = ast_Arguments(node, st)
        node.out_arguments = ast_Arguments(node, st)
        nodes.append(node)

    return nodes

def ast_Events(parent, yamltree) -> list[Event]:
    subtrees = get_optional_yaml_value(yamltree, 'events')

    # (Optional)
    if subtrees is None:
       return []
    require_list(subtrees, 'events')

    nodes = []
    for st in subtrees:
        node = Command(get_yaml_value(st, 'name'), parent)
        node.description = get_yaml_value(st, 'description')
        node.in_arguments = ast_Arguments(node, st)
        nodes.append(node)

    return nodes

def ast_Interfaces(parent, yamltree) -> list[Interface]:
    subtrees = get_yaml_value(yamltree, 'interfaces')
    require_list(subtrees, 'interfaces')

    nodes = []
    for st in subtrees:
        # Workaround for WIP definition of includes.  Skip the includes
        if get_optional_yaml_value(st, 'include-interface') is None:
            node = Interface(get_yaml_value(st, 'name'), parent)
            node.description = get_yaml_value(st, 'description')
            node.commands = ast_Commands(node, st)
            node.methods = ast_Methods(node, st)
            node.events = ast_Events(node, st)
            nodes.append(node)

    return nodes

def ast_Service(parent, yamltree) -> Service:

    # Look into subtree.  We expect only one 'service:' node per given
    # tree when we reach this function.   (NOTE: is that correct for the future?)
    subtree = get_yaml_value(yamltree, 'service')

    # We need the name to construct an anytree object, so AST
    # constructor requires it too.
    # For here, we use the service name as anytree node name.
    # (For other item types that are anonymous in the tree because they have no
    # name spcified, then the item type is used as node name instead)
    node = Service(get_yaml_value(subtree, 'name'), parent)

    # After creating the node we simply assign other member attributes directly

    # Keep recursing into the child objects (but only the specific types
    # that are expected in a valid file
    # So for a  service we expect datatypes and interfaces as children:
    node.description = get_yaml_value(subtree, 'description')
    node.datatypes = ast_Datatypes(node, subtree)
    node.interfaces = ast_Interfaces(node, subtree)

    return node

# Build the AST from the parsed YAML starting at the root.
def ast_Root(yamltree):

    # Let's have an "empty" root node at the top, called "/"
    # This later allows for putting more than one Service node below it
    # when reading multiple files.
    root = AST("", None)

    try:
        # Only expecting one service per tree at the moment
        # Add it under the root node.  The rest of the tree is attached
        # as children to the service node by the other functions.
        s = ast_Service(root, yamltree)

    except ASTNodeError:
        print("AST Node Exception, FIXME")

    return root

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

