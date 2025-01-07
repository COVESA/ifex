# SPDX-License-Identifier: MPL-2.0
# ----------------------------------------------------------------------------
# (C) 2021 COVESA
# Generator module
# These are general functions or convenience functions that can be used
# by specific generators and other tools, or it may serve as an example.
# ----------------------------------------------------------------------------

"""
IFEX code-generation functions
"""

# This performs the following related functions:

# 1. As input.yaml we expect an AST as provided by the parser module
#
# 2. It uses jinja2 templating library to generate code or configuration
#    according to given templates.

# For other features from parser module
from typing import Any
from ifex.templates import JinjaTemplateEnv

# Module global - probably soon to be modified to run-time instantiation of a
# JinjaTemplateEnv instance instead.
jinja_env = JinjaTemplateEnv.JinjaTemplateEnv("simple")

# Exception:
class GeneratorError(BaseException):
    def __init__(self, m):
        self.msg = m

# ---------- GENERATION FUNCTIONS ------------

# gen() function to be called from templates
def gen(node : Any, template_file = None):
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
            return jinja_env.get_template(template_file).render({'item' : node})
        else:
            print(f'node is of type {type(node)}, second arg is of type {type(template_file)}  ({type(template_file).__class__}, {type(template_file).__class__.__name__})')
            raise GeneratorError(f'Wrong use of gen() function! Usage: pass the node as first argument (you passed a {type(node)}), and optionally template name (str) as second argument. (You passed a {template_file.__name__})')

# gen helper function:
def _gen_with_default_template(node : Any):

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
        raise GeneratorError(f'The template seems to call gen() with an unknown field name: node {node} is of type StrictUndefined. Please check!')
        return ""

    # Plain types -> print as-is
    if isinstance(node, (str, int, float)):
        return node

    # Complex types -> use the corresponding template for the type
    tpl = jinja_env.get_default_template_file(nodetype)
    if tpl is None:
        raise GeneratorError(f"gen() function called with node of type '{nodetype}' but no default template is defined for this type.")
    else:
        return jinja_env.get_template(tpl).render({'item' : node})

#  Alternative functions, for unit testing

# Instead of providing a template file, provide the template text itself
# (for unit tests mostly).  See gen() for more comments/explanation.
def gen_template_text(node: Any, template_text: str):
   # Processing of lists of objects, see gen() for explanation
   if type(node) == list or type(node) == tuple:
       return [gen_template_text(x, template_text) for x in node]
   if template_text is None:
       raise GeneratorError(f'gen_template_text called without template')
   elif type(template_text) == str:
       return jinja_env.render_template(template_text,{'item' : node})
   else:
       print(f'node is of type {type(node)}, second arg is of type {type(template_text)}  ({type(template_text).__class__}, {type(template_text).__class__.__name__})')
       raise GeneratorError(f'Wrong use of gen() function! Usage: pass the node as first argument (you passed a {type(node)}), and optionally template name (str) as second argument. (You passed a {template_text.__name__})')

# Entry point for passing a dictionary of variables instead:
def gen_dict_with_template_file(variables : dict, templatefile):
    return get_template(templatefile).render(variables)

# Export the gen() function and classes into jinja template land
# so that they can be referred to inside templates.
jinja_env.set_template_env(gen=gen)

# ----------------------------------------------------------------
# MAIN = Standalone test Code only, not normal use.
import sys
from models.ifex.ifex_parser import get_ast_from_yaml_file
if __name__ == '__main__':
    yaml_file = sys.argv[1]
    template_dir = sys.argv[2]
    ast = get_ast_from_yaml_file(yaml_file)
    # re-initialize jinja environment with the given template dir
    jinja_env.__init__(template_dir)
    jinja_env.set_template_env(gen=gen)
    print(gen(ast))
