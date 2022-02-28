# SPDX-License-Identifier: MPL-2.0
# ----------------------------------------------------------------------------
# (C) 2021 COVESA
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
from vsc_parser import AST, Argument, Method, Event, Member, Option, Namespace, Service
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

def gen(node : AST, second = None):

   # Processing of lists of objects
   if type(node) == list or type(node) == tuple:
       # Generate each node and return a list of results.
       # A list is not intended to be printed directly as output, but to be
       # processed by a jinja filter, such as |join(', ')
       return [gen(x, second) for x in node]

   # OK, now dispatch gen() depending on the input type
   if second is None:          # No explicit template -> use default for the node type
       return _gen_type(node)
   elif type(second) == str:   # Explicit template -> use it
       return _gen_tmpl(node, second)
   else:
      print(f'node is of type {type(node)}, second arg is of type {type(second)}  ({type(second).__class__}, {type(second).__class__.__name__})')
      raise GeneratorError(f'Wrong use of gen() function! Usage: pass the node as first argument (you passed a {type(node)}), and optionally template name (str) as second argument. (You passed a {second.__name__})')

# Implementation of typed variants of gen():

# If no template is specified, use the default template for the node type.
# A default template must be defined for this node type to use the function
# this way.
def _gen_type(node : AST):
    nodetype=type(node).__name__
    tpl = default_templates.get(nodetype)
    if tpl is None:
       raise GeneratorError(f'gen() function called with node of type {nodetype} but no default template is defined for the type {nodetype}')
    else:
       return get_template(tpl).render({ 'item' : node})

# If template name directly specified, just use it.
def _gen_tmpl(node : AST, templatefile: str):
    return get_template(templatefile).render({ 'item' : node})

#  Alternative functions, for unit testing

# Instead of providing a template file, provide the template text itself
# (for unit tests mostly).  See gen() for more comments/explanation.
def _gen_with_text_template(node: AST, second: str):
   # Processing of lists of objects, see gen() for explanation
   if type(node) == list or type(node) == tuple:
      return [_gen_with_text_template(x, second) for x in node]
   if second is None:
       return _gen_type(node)
   elif type(second) == str:  # "second" is here the template text, not a filename
       return jinja2.Template(second).render({'item' : node})
   else:
      print(f'node is of type {type(node)}, second arg is of type {type(second)}  ({type(second).__class__}, {type(second).__class__.__name__})')
      raise GeneratorError(f'Wrong use of gen() function! Usage: pass the node as first argument (you passed a {type(node)}), and optionally template name (str) as second argument. (You passed a {second.__name__})')


# Entry point for passing a dictionary of variables instead:
def gen_dict_with_template_file(variables : dict, templatefile):
    return get_template(templatefile).render(variables)

# Export the gen() function and classes into jinja template land
# so that they can be referred to inside templates.

jinja_env.globals.update(
 gen=gen,
 AST=AST,
 Argument=Argument,
 Method=Method,
 Event=Event,
 Member=Member,
 Option=Option,
 Namespace=Namespace,
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

