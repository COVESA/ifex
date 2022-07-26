# SPDX-License-Identifier: MPL-2.0
# ----------------------------------------------------------------------------
# (C) 2021 COVESA
# Test code for code generator part of VSC tools
# ----------------------------------------------------------------------------
# This is maybe not ideal way but seems efficient enough
import os.path

from model import vsc_parser, vsc_generator, ast
from pathlib import Path
import sys

proj_root = Path(__file__).parents[1]
sys.path.append(os.path.join(proj_root, "model"))

def test_x():
    assert 1 == 1


def test_gen():
    # The files named 'input.yaml', 'template' and 'result' are in the tests directory
    ast_root = vsc_parser.get_ast_from_file('input.yaml')

    with open("template", "r") as template_file:
        generated = vsc_generator._gen_with_text_template(ast_root, template_file.read())

    with open("result", "r") as result_file:
        # Apparently we must strip newline or it will be added superfluously here
        # even if it is not in the file. The same does not happen on the
        # jinja-template generation we are comparing to.
        wanted = result_file.read().rstrip()
        assert generated == wanted


def test_ast_gen():
    ast_tmp = ast.read_ast_from_yaml_file('input.yaml')

    assert ast_tmp.service.name == "service_name"
    assert ast_tmp.service.major_version == 3
    assert ast_tmp.service.minor_version == 0


def test_ast_manual():
    namespace = ast.Namespace(name='test', description='test', major_version=1, minor_version=0)
    service = ast.Service(name='test', description='test', major_version=1, minor_version=0, namespaces=[namespace])
    ast_root = ast.AST(service=service)

    assert ast_root.service.name == 'test'
    assert ast_root.service.major_version == 1
    assert ast_root.service.minor_version == 0
    assert ast_root.service.namespaces[0].name == 'test'

# Unused
default_templates = {}

# TODO: Loop over subdirectories in tests to perform tests for different
# 'input.yaml/template/result' files
