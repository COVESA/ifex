# SPDX-License-Identifier: MPL-2.0
# ----------------------------------------------------------------------------
# (C) 2021 COVESA
# Test code for code generator part of VSC tools
# ----------------------------------------------------------------------------

import pytest

# This is maybe not ideal way but seems efficient enough
from pathlib import Path
import sys
proj_root = Path(__file__).parents[1]
sys.path.append(str(proj_root) + "/model")

import vsc_parser, vsc_generator

def test_x():
    assert 1 == 1

def test_gen():
    # The files named 'input', 'template' and 'result' are in the tests directory
    ast = vsc_parser.get_ast_from_file('input')

    with open("template", "r") as templatefile:
        generated = vsc_generator._gen_with_text_template(ast, templatefile.read())

    with open("result", "r") as resultfile:
        # Apparently we must strip newline or it will be added superfluously here
        # even if it is not in the file. The same does not happen on the
        # jinja-template generation we are comparing to.
        wanted = resultfile.read().rstrip()
        assert generated == wanted

# Unused
default_templates = {
}

# TODO: Loop over subdirectories in tests to perform tests for different
# 'input/template/result' files
