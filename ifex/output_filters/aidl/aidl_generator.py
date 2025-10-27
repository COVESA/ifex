# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project
# vim: tw=120 ts=4 et

"""
Render an AIDL AST (list of AIDLFile objects) to text using Jinja2 templates.

Public API:
    aidl_file_to_text(aidl_file: AIDLFile) -> str
        Render a single AIDLFile to its .aidl text representation.

    aidl_to_text(aidl_files: List[AIDLFile]) -> str
        Render all files, separated by a filename header comment.

Note: We build the Jinja2 environment directly rather than using JinjaSetup,
because JinjaSetup's template-discovery relies on ifex_ast_doc.walk_type_tree()
which cannot traverse Union type annotations.  The AIDL AST uses a Union for
AIDLFile.declaration, so we map templates manually by class name.
"""

import jinja2
import os
from typing import List
from ifex.models.aidl.aidl_ast import AIDLFile

_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")


def _build_jinja_env(template_dir: str) -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=jinja2.select_autoescape([]),
        undefined=jinja2.StrictUndefined,
    )
    env.trim_blocks = True
    env.lstrip_blocks = True
    return env


def _make_gen(env: jinja2.Environment):
    """Return a gen() closure that dispatches to the template named after the node's class."""
    def gen(node):
        class_name = type(node).__name__
        template_file = class_name + ".j2"
        try:
            template = env.get_template(template_file)
        except jinja2.TemplateNotFound:
            raise ValueError(f"No AIDL template found for node type '{class_name}' "
                             f"(expected '{template_file}' in {env.loader.searchpath})")
        return template.render(item=node)
    return gen


def aidl_file_to_text(aidl_file: AIDLFile, template_dir: str = _TEMPLATE_DIR) -> str:
    """Render one AIDLFile to its .aidl source text."""
    env = _build_jinja_env(template_dir)
    gen = _make_gen(env)
    env.globals["gen"] = gen
    return gen(aidl_file).rstrip() + "\n"


def aidl_to_text(aidl_files: List[AIDLFile], template_dir: str = _TEMPLATE_DIR) -> str:
    """Render a list of AIDLFile objects.

    Each file is preceded by a comment header showing its filename, making the
    combined output easy to split into individual files later.
    """
    parts = []
    for f in aidl_files:
        parts.append(f"// ----- {f.filename} -----")
        parts.append(aidl_file_to_text(f, template_dir))
    return "\n".join(parts)
