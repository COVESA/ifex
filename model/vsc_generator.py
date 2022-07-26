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

# 1. As input.yaml we expect an AST as provided by the parser module
#
# 2. It uses jinja2 templating library to generate code or configuration
#    according to given templates.

# It's useful to have these classes in our namespace directly
from model.vsc_parser import AST, Argument, Enum, Error, Event, Include, Member, Method, Namespace, Option, Property, Service, Struct, Typedef

from model import vsc_parser # For other features from parser module
import anytree
import getopt
import jinja2
import os
import sys

# Set up Jinja
jinja_env = jinja2.Environment(
        # Use the subdirectory 'templates' relative to this file's location
        loader=jinja2.FileSystemLoader(os.path.dirname(os.path.join(os.path.realpath(__file__), '/../templates'))),

        # Templates with these extension gets automatic autoescape for HTML
        # It's more annoying for code generation, so passing empty list for now.
        autoescape=jinja2.select_autoescape([])
        )

# We want the control blocks in the template to NOT result in any extra
# white space when rendering templates. However, this might be a choice
# made by each generator, so we need to export the ability to keep these
# settings public for other code to modify them.
jinja_env.trim_blocks = True
jinja_env.lstrip_blocks = True
jinja_env.undefined = jinja2.StrictUndefined

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
    # Processing of lists of objects?
    if type(node) == list or type(node) == tuple:
        # Generate each node and return a list of results. A list is not
        # intended to be printed directly as output, but to be processed by
        # a jinja filter, such as |join(', ')

        if len(node) == 0:
            return []
        else:
            # Recurse over each item in list, and return a list of strings
            # that is generated for each one.
            return [gen(x, second) for x in node]

    else:
        # Processing single item!
        # second argument is either an explicit template, or None. If it is
        # None, then the node type will be used to determine the template.
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
    # It is currently unexpected to receive None.  But minor changes might
    # change this later.  An alternative is to generate an empty string,
    # but for now let's make sure this case is noticed with an exception,
    # so it can be investigated.
    if node is None:
        raise GeneratorError(f"Unexpected 'None' node received")
        return ""

    nodetype=type(node).__name__

    # If the output-template refers to a member variable that was _not
    # defined_ in the node, then it shows up as Undefined type. This
    # happens when optional things do not appear within the service
    # definition. We just generate empty strings for those items.
    if nodetype == "Undefined":
        return ""

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

# The AST class definitions are not required to reference the member
# variables on objects, so they will be rarely used.  But possibly some
# template will have logic to create an AST node on-the-fly and then call
# the generator on it, and this will require knowledge of the AST
# (sub)class.

jinja_env.globals.update(
        gen=gen,  # Most common function to reference from template
        AST=AST,  # AST classes and subclasses....
        Argument=Argument,
        Enum=Enum,
        Error=Error,
        Event=Event,
        Include=Include,
        Member=Member,
        Method=Method,
        Namespace=Namespace,
        Option=Option,
        Property=Property,
        Service=Service,
        Struct=Struct,
        Typedef=Typedef)

# This code file can be used in two ways.  Either calling this file as a
# program using the main entry points here, and specifying input.yaml parameter.
# Alternatively, for more advanced usage, the file might be included as a
# module in a custom generator implementation.  That implementation is
# likely to call some of the funcctions that were defined above.

# For the first case, here follows the main entry points and configuration:

def usage():
    print("usage: generator.py <input.yaml-yaml-file (path)> <output-template-file (name only, not path)>")
    sys.exit(1)

# This is a default definition for our current generation tests.
# It may need to be changed, or defined differently in a custom generator
default_templates = {
        'Service' : 'Service-simple_doc.html',
        'Argument' : 'Argument-simple_doc.html'
        }

# If run as a script, generate a single YAML file using a single root template
if __name__ == "__main__":
    if not len(sys.argv) == 3:
        usage()
    ast = vsc_parser.get_ast_from_file(sys.argv[1])
    templatename = sys.argv[2]
    print(gen(ast, templatename))

