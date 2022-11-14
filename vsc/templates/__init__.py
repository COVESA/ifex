# SPDX-FileCopyrightText: Copyright (c) 2022 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

import os
import jinja2
from typing import Dict, Any

TemplatePath = os.path.dirname(os.path.realpath(__file__))

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

# This is a default definition for our current generation tests.
# It may need to be changed, or defined differently in a custom generator
default_templates = {
        'AST': 'AST-simple_doc.tpl',
        'Service': 'Service-simple_doc.html',
        'Argument': 'Argument-simple_doc.html',
        'Error': 'Error-simple_doc.html',
        'Member': 'Member-simple_doc.html',
        'Namespace': 'Namespace-simple_doc.html',
        'Argument': 'Argument-simple_doc.html'
        }

# wrapper over jinja2 render
def render_template(text: str, env: Dict[Any,Any]):
    return jinja2.Template(text).render(env);

# wrapper over jinja2 to export environment.
def set_template_env(**kwargs):
    jinja_env.globals.update(kwargs)
    
# gets template by name from the list of default_templates.
def get_default_template(name):
    return default_templates.get(name)

# Get template with given name (search path should be handled by the loader)
def get_template(filename):
    return jinja_env.get_template(filename)
