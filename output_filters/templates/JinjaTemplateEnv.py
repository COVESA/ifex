# SPDX-FileCopyrightText: Copyright (c) 2022 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

import os
import jinja2
from typing import Dict, Any
from output_filters.templates import TemplateDir

class JinjaTemplateEnv:

    tpath = ""
    default_templates = {}
    jinja_env = None

    def __init__(self, directory=""):
        tpath = TemplateDir.abs_template_path(directory)

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
        self.default_templates = TemplateDir.find_matching_template_files(tpath)


    # wrapper over jinja2 render
    def render_template(self, text: str, env: Dict[Any,Any]):
        return jinja2.Template(text).render(env);

    # wrapper over jinja2 to export environment.
    def set_template_env(self, **kwargs):
        self.jinja_env.globals.update(kwargs)
        
    # gets template by name from the list of default_templates.
    def get_default_template_file(self, name):
        return self.default_templates.get(name)

    # Get template text for given name (search path should be handled by the loader)
    def get_template(self, filename):
        return self.jinja_env.get_template(filename)


# Test code
if __name__ == '__main__':
    x = JinjaTemplateEnv("simple")
    print(f"{x.default_templates}")

