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

import anytree
import getopt
import jinja2
import os
import parser
import sys

# Set up Jinja
jinja_env = jinja2.Environment(
        # Use the subdirectory 'templates' relative to this file's location
        loader =
        jinja2.FileSystemLoader(os.path.dirname(os.path.realpath(__file__)) + '/../templates'),

        # *IF* this might be used to generate HTML or XML
        # then templates with this extension gets automatic autoescape,
        # others should not.
        autoescape = jinja2.select_autoescape(['html', 'xml'])
        )

# This is important. We want the control blocks in the template to NOT
# result in any extra white space when rendering templates.
# However, this might be a choice made by each generator, so then we need
# to export the ability to keep these public for the using code to modify
# them.
jinja_env.trim_blocks = True
jinja_env.lstrip_blocks = True

# Get template with given name (search path should be handled by the loader)
def get_template(filename):
    return jinja_env.get_template(filename)

def render_dict_with_template_file(variables : dict, templatefile):
    return get_template(templatefile).render(variables)

def render_ast_with_template_file(ast : parser.AST, templatefile):
    r = anytree.Resolver()
    return get_template(templatefile).render({ 'root' : ast})

# ---------- TEST / SIMPLE USAGE ------------

def usage():
    print("usage: generator.py <input-yaml-file (path)> <output-template-file (name only, not path)>")
    sys.exit(1)

def test(argv):
    if not len(argv) == 3:
        usage()
    ast = parser.get_ast_from_file(argv[1])
    print(render_ast_with_template_file(ast, argv[2]))

# If run as a script, generate a single YAML file and single template 
# (for testing)
if __name__ == "__main__":
    # execute only if run as a script
    test(sys.argv)

# TEST: Get AST representation of service, and render it with a simple
# template

