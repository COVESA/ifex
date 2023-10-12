# SPDX-FileCopyrightText: Copyright (c) 2022 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

from models.ifex import ifex_ast
from models.ifex import ifex_ast_doc
import os
import sys

# Needed globally by setup.py
TemplatePath = os.path.dirname(os.path.realpath(__file__))

def find_matching_template_files(directory : str, recurse = False, absolute = False):
    """Search in given directory to find any files that match (start with) any of the given class names.
    Return a dict that maps each class name to its corresponding template file name.
    If there is more than one matching file, the last found one will remain in result."""

    classes = ifex_ast.get_ast_node_type_names()

    templates = {}  # Dict maps node name to the template file name
    if recurse:
        for _, _, filenames in os.walk(directory):
            for fn in filenames:
                for n in classes:
                    if fn.startswith(n):
                        # here absolute path is assumed since we're iterating over possibly multiple sub-directories
                        templates[n] = os.path.join(root, fn)
    else: # non recursive
        for fn in os.listdir(directory):
            for n in classes:
                if fn.startswith(n):
                    if absolute:
                        templates[n] = os.path.join(directory, fn)
                    else:
                        templates[n] = fn
    return templates

def abs_template_path(p):
    """ Convert relative or absolute path p into an absolute path pointing to a template directory """
    if os.path.isabs(p):
        return p
    else:
        # Relative to this file (i.e. template root)
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), p)

# Some test code - print out result from template-dir as arg
if __name__ == '__main__':
    template_dir = sys.argv[1]
    if not os.path.isabs(template_dir):
        # Relative to this file (i.e. template root)
        template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), template_dir)

    print("Relative dirs:\n")
    print(find_matching_template_files(template_dir))
    print("\nAbsolute dirs:\n")
    print(find_matching_template_files(template_dir, False, True))

