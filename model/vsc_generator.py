# ----------------------------------------------------------------------------
# Generator module
# These are general functions or convenience functions that can be used
# by specific generators and other tools, or it may serve as an example.
# ----------------------------------------------------------------------------

"""
VSC code-generation functions
"""

# This performs the following related functions:

# 1. As input we expect an AST as provided by the parser module
#
# 2. It uses jinja2 templating library to generate code or configuration
#    according to given templates.

# It's useful to have these classes in our namespace directly
from vsc_parser import AST, Argument, Command, Method, Event, Interface, Member, Option, Type, Namespace, Datatypes, Service
import vsc_parser # For other features from parser module
import anytree
import getopt
import jinja2
import os
import sys

# Set up Jinja
jinja_env = jinja2.Environment(
        # Use the subdirectory 'templates' relative to this file's location
        loader =
        jinja2.FileSystemLoader(os.path.dirname(os.path.realpath(__file__)) + '/../templates'),

        # Templates with these extension gets automatic autoescape for HTML
        # It's more annoying for code generation, so passing empty list for now.
        autoescape = jinja2.select_autoescape([])
        )

# This is important. We want the control blocks in the template to NOT
# result in any extra white space when rendering templates.
# However, this might be a choice made by each generator, so then we need
# to export the ability to keep these public for the using code to modify
# them.
jinja_env.trim_blocks = True
jinja_env.lstrip_blocks = True

default_templates = {}

# Exception:
class GeneratorError(BaseException):
   def __init__(self, m):
       self.msg = m


# ---------- GENERATION FUNCTIONS ------------

# Get template with given name (search path should be handled by the loader)
def get_template(filename):
    return jinja_env.get_template(filename)

# Frontend to overloaded gen() function:

def gen(node : AST, second):

   # Processing of lists of objects
   if type(node) == list or type(node) == tuple:
      # Generate each node and return a list of results.
      # A list is not intended to be printed directly as output, but to be
      # processed by a jinja filter, such as |join(', ')
      return [gen(x, second) for x in node]

   # OK, now dispatch gen() depending on the input type
   if type(second) is type and issubclass(second, AST):
       return _gen_type(node, second)
   elif type(second) == str:
       return _gen_tmpl(node, second)
   else:
      print(f'node is of type {type(node)}, second is of type {type(second)}  ({type(second).__class__}, {type(second).__class__.__name__})')
      raise GeneratorError(f'Wrong use of gen() function! Usage: pass the node as first argument (you passed a {type(node)}), and a Type (must be AST subclass)  or template name as second argument. (You passed a {second.__name__})')

# Implementation of typed variants of gen():

# If type specified, use the default template for that type.  It must be
# defined for this node type to use the function this way.
def _gen_type(node : AST, nodetype : type):
    tpl = default_templates.get(nodetype.__name__)
    if tpl is None:
       raise GeneratorError(f'gen() function called with node of type {nodetype.__name__} but no default template is defined for the type {nodetype.__name__}')
    else:
       return get_template(tpl).render({ 'item' : node})

# If template name directly specified, just use it.
def _gen_tmpl(node : AST, templatefile: str):
    return get_template(templatefile).render({ 'item' : node})

# Entry point for passing a dictionary of variables instead:
def gen_dict_with_template_file(variables : dict, templatefile):
    return get_template(templatefile).render(variables)

# Export the gen() function and classes into jinja template land
# so that they can be referred to inside templates.

jinja_env.globals.update(
 gen=gen,
 AST=AST,
 Argument=Argument,
 Command=Command,
 Method=Method,
 Event=Event,
 Interface=Interface,
 Member=Member,
 Option=Option,
 Type=Type,
 Namespace=Namespace,
 Datatypes=Datatypes,
 Service=Service)

# ---------- TEST / SIMPLE USAGE ------------

def usage():
    print("usage: generator.py <input-yaml-file (path)> <output-template-file (name only, not path)>")
    sys.exit(1)

def test(argv):
    if not len(argv) == 3:
        usage()
    ast = vsc_parser.get_ast_from_file(argv[1])
    print(gen(ast, argv[2]))

# TEMP TEST TO BE MOVED
default_templates = {
        'Service' : 'Service-simple_doc.html',
        'Argument' : 'Argument-simple_doc.html'
        }

# If run as a script, generate a single YAML file and single template
# (for testing)
if __name__ == "__main__":
    # execute only if run as a script
    test(sys.argv)

