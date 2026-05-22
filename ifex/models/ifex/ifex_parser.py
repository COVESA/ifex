# SPDX-License-Identifier: MPL-2.0
# ----------------------------------------------------------------------------
# (C) 2021 COVESA
# Reader/parser module
# To be used by all generators and other tools
# ----------------------------------------------------------------------------

"""
VSC parser/reader to be used by generators and other tools
"""

# This is now a small wrapper around ifex_ast.py
# In fact, it seems likely that this file should be removed since it has
# almost no function left.

import yaml, dacite
from typing import Dict, Any
from ifex.models.ifex.ifex_ast import AST, Namespace


def _expand_dot_namespace(ns: Namespace) -> Namespace:
    """Expand a dot-separated namespace name into nested Namespace objects.

    ``name: A.B.C`` is equivalent to nesting::

        name: A
          namespaces:
            - name: B
              namespaces:
                - name: C
                  ...content...

    Children are expanded recursively before wrapping.
    """
    expanded_children = [_expand_dot_namespace(child) for child in (ns.namespaces or [])]

    parts = ns.name.split(".")
    if len(parts) == 1:
        ns.namespaces = expanded_children
        return ns

    # Innermost namespace carries all content from the dot-path namespace
    inner = Namespace(
        name=parts[-1],
        description=ns.description,
        major_version=ns.major_version,
        minor_version=ns.minor_version,
        version_label=ns.version_label,
        events=ns.events,
        methods=ns.methods,
        typedefs=ns.typedefs,
        includes=ns.includes,
        structs=ns.structs,
        enumerations=ns.enumerations,
        properties=ns.properties,
        namespaces=expanded_children,
        interface=ns.interface,
    )

    # Wrap in empty intermediate layers
    for part in reversed(parts[:-1]):
        inner = Namespace(name=part, namespaces=[inner])

    return inner


def read_yaml_file(filename) -> str:
    """
    Tries to read a file which contains yaml into a string
    TODO: can have performance implications when file size is big. We have to consider incremental yaml processing.
    :param filename:
    :return: file contents as string
    """
    with open(filename, 'r') as yaml_file:
        return yaml_file.read()


def parse_yaml_file(yaml_string: str) -> Dict[Any, Any]:
    """
    Tries to parse yaml into a python dictionary
    :param yaml_string: String containing text in YAML format
    :return: Dictionary
    """
    return yaml.safe_load(yaml_string)


def get_ast_from_yaml_file(filename: str) -> AST:
    """
    Reads a yaml file and returns AST
    :param filename: path to a yaml file
    :return: abstract syntax tree (vehicle service catalog)
    """

    yaml_string = read_yaml_file(filename)

    yaml_dict = parse_yaml_file(yaml_string)

    try:
        #cfg = dacite.Config(strict=True) # Fail if unknown keys in dict
        cfg = dacite.Config(strict=False) # Fail if unknown keys in dict
        ast = dacite.from_dict(data_class=AST, data=yaml_dict, config=cfg)
        ast.namespaces = [_expand_dot_namespace(ns) for ns in (ast.namespaces or [])]
        return ast
    except dacite.UnexpectedDataError as e:
        print(f"ERROR: Read error resulting from {filename}: {e}")
        raise e
