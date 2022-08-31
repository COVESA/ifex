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

# 1. As input.yaml we expect an Namespace as provided by the parser module
#
# 2. It uses jinja2 templating library to generate code or configuration
#    according to given templates.

# For other features from parser module
from vsc.model import vsc_ast
from vsc.model.vsc_ast import Namespace
from vsc.templates import TemplatePath
import jinja2
import sys

# Set up Jinja
jinja_env = jinja2.Environment(
        # Use the subdirectory 'templates' relative to this file's location
        loader=jinja2.FileSystemLoader(TemplatePath),

        # Templates with these extension gets automatic auto escape for HTML
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

# gen() function to be called from templates
def gen(node : Namespace, template_file = None):
    # Processing of lists of objects?

    if node is None:
       return "NONE"

    if isinstance(node, (list,tuple)):
        # Generate each node and return a list of results. A list is not
        # intended to be printed directly as output, but to be processed by
        # a jinja filter, such as |join(', ')
        return [gen(x, template_file) for x in node]
    else:
        # No explicit template -> use default for the node type
        if template_file is None:
            return _gen_with_default_template(node)
        elif type(template_file) == str:   # Explicit template file -> use it
            return get_template(template_file).render({'item' : node})
        else:
            print(f'node is of type {type(node)}, second arg is of type {type(template_file)}  ({type(template_file).__class__}, {type(template_file).__class__.__name__})')
            raise GeneratorError(f'Wrong use of gen() function! Usage: pass the node as first argument (you passed a {type(node)}), and optionally template name (str) as second argument. (You passed a {template_file.__name__})')

# gen helper function:
def _gen_with_default_template(node : Namespace):

    # None is for a field that exists in Namespace definition, but was not given
    # a value in the YAML (=> happens only if it was an optional item).
    if node is None:
        # FIXME: This should be expected behavior and should return empty string, 
        # but let's first debug to see when it happens:
        raise GeneratorError(f"_gen_type(): Unexpected 'None' node received")

    # StrictUndefined is for an *unknown* field mentioned in the Jinja template
    # (misspelling, etc.)
    nodetype=type(node).__name__
    if nodetype == 'StrictUndefined':
        raise GeneratorError(f'The template seems to call gen() with an unknown field name. Please check!')
        return ""

    # Plain types -> print as-is
    if isinstance(node, (str, int, float)):
        return node

    # Complex types -> use the corresponding template for the type
    tpl = default_templates.get(nodetype)
    if tpl is None:
        raise GeneratorError(f"gen() function called with node of type '{nodetype}' but no default template is defined for this type.")
    else:
        return get_template(tpl).render({'item' : node})

#  Alternative functions, for unit testing

# Instead of providing a template file, provide the template text itself
# (for unit tests mostly).  See gen() for more comments/explanation.
def gen_template_text(node: Namespace, template_text: str):
   # Processing of lists of objects, see gen() for explanation
   if type(node) == list or type(node) == tuple:
       return [gen_template_text(x, template_text) for x in node]
   if template_text is None:
       raise GeneratorError(f'gen_template_text called without template')
   elif type(template_text) == str:
       return jinja2.Template(template_text).render({'item' : node})
   else:
       print(f'node is of type {type(node)}, second arg is of type {type(template_text)}  ({type(template_text).__class__}, {type(template_text).__class__.__name__})')
       raise GeneratorError(f'Wrong use of gen() function! Usage: pass the node as first argument (you passed a {type(node)}), and optionally template name (str) as second argument. (You passed a {template_text.__name__})')

# Entry point for passing a dictionary of variables instead:
def gen_dict_with_template_file(variables : dict, templatefile):
    return get_template(templatefile).render(variables)

# Export the gen() function and classes into jinja template land
# so that they can be referred to inside templates.
jinja_env.globals.update(gen=gen)


def usage():
    print("usage: generator.py <input.yaml-file (path)> <output-template-file (name only, not path)>")
    sys.exit(1)

# This is a default definition for our current generation tests.
# It may need to be changed, or defined differently in a custom generator
default_templates = {
        'Namespace': 'Namespace-simple_doc.tpl',
        'Service': 'Service-simple_doc.html',
        'Argument': 'Argument-simple_doc.html',
        'Error': 'Error-simple_doc.html',
        'Member': 'Member-simple_doc.html',
        'Namespace': 'Namespace-simple_doc.html',
        'Argument': 'Argument-simple_doc.html'
        }

# If run as a script, generate a single YAML file using a single root template
if __name__ == "__main__":
    if not len(sys.argv) == 3:
        usage()
    ast = vsc_ast.read_ast_from_yaml_file(sys.argv[1])
    templatename = sys.argv[2]
    print(gen(ast, templatename))

