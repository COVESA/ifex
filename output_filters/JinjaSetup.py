# SPDX-FileCopyrightText: Copyright (c) 2025 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

import jinja2
import os
from models.ifex import ifex_ast_doc
from typing import Dict, Any

# Exception:
class GeneratorError(BaseException):
    def __init__(self, m):
        self.msg = m

class TemplateFinder:
    def __init__(self, name):
        self.classes_list = None

    # collector: Small helper that grabs each output from the walk
    # function, and in the process converting each class object to its
    # name string Reusing type_name() from ifex_ast_doc takes care of
    # ForwardRef type correctly.

    # Create a closure around the classes_list variable
    def create_collector(self):
        self.classes_list = set() # Reset
        return lambda x : self.classes_list.add(ifex_ast_doc.type_name(x))

    def reset_collector(self):
        self.classes_list = set()

    def find_matching_template_files(self, directory : str, root_ast_class, recurse = False, absolute = False):
        """Search in given directory to find any files that match (start with) any of the given class names.
        Return a dict that maps each class name to its corresponding template file name.
        If there is more than one matching file, the last found one will remain in result."""
        # Reuse walk_type_tree() from documentation generator, which gives us each of the
        # node classes in the ifex AST definition.  More correctly, its like the
        # visitor pattern, so the function we provide (collector) will be called once
        # for each found class.

        collector = self.create_collector()
        ifex_ast_doc.walk_type_tree(root_ast_class, collector, {})

        # Now all classes are collected in the classes_list variable
        classes = self.classes_list

        templates = {}  # Dict maps node name to the template file name
        if recurse:
            for _,_,filenames in os.walk(directory):
                for ff in filenames:
                    for n in classes:
                        if ff.startswith(n + '.'):
                            templates[n] = os.path.join(root, ff)
        else: # non recursive
            for ff in os.listdir(directory):
                for n in classes:
                    if ff.startswith(n + '.'):
                        if absolute:
                            templates[n] = os.path.join(directory, ff)
                        else:
                            templates[n] = ff
        return templates


# A class to hold our Jinja environment, as well as the table of default
# templates for every node type.
class JinjaTemplateEnv:
    tpath = ""
    default_templates = {}
    jinja_env = None

    def __init__(self, root_node, template_dir_abs):
        tpath = template_dir_abs

        # Set up Jinja
        self.jinja_env = jinja2.Environment(
                # Use the subdirectory 'templates' relative to this file's location
                loader=jinja2.FileSystemLoader(tpath),

                # Templates with these extension gets automatic auto escape for HTML
                # It's more annoying for code generation, so passing empty list for now.
                autoescape=jinja2.select_autoescape([])
                )

        # We want the control blocks in the template to NOT result in any extra
        # white space when rendering templates. However, this might be a choice
        # made by each generator, so we need to export the ability to keep these
        # settings public for other code to modify them.
        self.jinja_env.trim_blocks = True
        self.jinja_env.lstrip_blocks = True
        self.jinja_env.undefined = jinja2.StrictUndefined

        # This is a default definition for our current generation tests.
        # It may need to be changed, or defined differently in a custom generator

        tfinder = TemplateFinder("generator-from-ifex")
        self.default_templates = tfinder.find_matching_template_files(tpath, root_node)


    # wrapper over jinja2 render
    def render_node(self, node):

        template_file = self.get_default_template_file(ifex_ast_doc.type_name(type(node)))
        if template_file is None:
            raise GeneratorError(f"gen() function called with node of type '{type(node)}' but no default template is defined for this type.")

        template = self.get_template(template_file)
        if template is None:
            raise GeneratorError(f'Failure to get actual template object from Jinja framework for {template_file=}')
        else:
            return template.render({"item" : node})

        return None


    # wrapper over jinja2 to export environment.
    def set_template_env(self, **kwargs):
        self.jinja_env.globals.update(kwargs)

    # gets template by name from the list of default_templates.
    def get_default_template_file(self, name):
        return self.default_templates.get(name)

    # Get template text for given name (search path should be handled by the loader)
    def get_template(self, filename):
        return self.jinja_env.get_template(filename)

    # Create a closure over the jinja environment so that gen() can be called
    # without any context except the node itself
    def create_gen_closure(self):
        def f(node):
            return self.render_node(node)
        return f


# Some test code - print out result from template-dir as arg
if __name__ == '__main__':
    import sys
    from models.ifex import ifex_ast

    if len(sys.argv) < 1:
        print("Usage (test) : python JinjaSetup.py <templatedir>")
        sys.exit(1)
    template_dir = sys.argv[1]

    # Test code - just output the templates under D-Bus for now
    reldir="templates/D-Bus"
    template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), reldir)

    tfinder = TemplateFinder("generator-from-ifex")
    print(f"TEST CODE!\nGetting templates from {template_dir=}\nRESULT:")
    print(tfinder.find_matching_template_files(template_dir, ifex_ast.AST))

