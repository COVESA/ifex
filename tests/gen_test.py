# SPDX-License-Identifier: MPL-2.0
# ----------------------------------------------------------------------------
# (C) 2021 COVESA
# Test code for code generator part of VSC tools
# ----------------------------------------------------------------------------
# This is maybe not ideal way but seems efficient enough
from vsc.model import vsc_ast, vsc_parser, vsc_generator
import dacite, pytest
import os

TestPath = os.path.dirname(os.path.realpath(__file__))

def test_x():
    assert 1 == 1

def test_gen():

    # Get matching dirs named 'test.<something>'
    for (_,dirs,_) in os.walk(TestPath):
        test_dirs = [ x for x in dirs if x.startswith('test.') ]
        break # First level of walk is enough.

    for subdir in test_dirs:
        print(f"Running test in {subdir}.")
        path = os.path.join(TestPath, subdir)

        # The files named 'input.yaml', 'template' and 'result' are in each test directory
        ast_root = vsc_parser.get_ast_from_file(os.path.join(path, 'input.yaml'))

        with open(os.path.join(path,"template"), "r") as template_file:
            generated = vsc_generator.gen_template_text(ast_root, template_file.read())

        with open(os.path.join(path,"result"), "r") as result_file:
            # Apparently we must strip newline or it will be added superfluously here
            # even if it is not in the file. The same does not happen on the
            # jinja-template generation we are comparing to.
            wanted = result_file.read().rstrip()
            assert generated == wanted


def test_ast_gen():
    service = vsc_parser.get_ast_from_file(os.path.join(TestPath, 'test.sample', 'input.yaml'))

    assert service.name == "named_service"
    assert service.major_version == 3
    assert service.minor_version == 0


def test_ast_manual():
    service = vsc_ast.AST(name='test', description='test', major_version=1, minor_version=0)

    assert service.name == 'test'
    assert service.description == 'test'
    assert service.major_version == 1
    assert service.minor_version == 0

# Test expected failed cases
def test_expected_raised_exceptions():

    # Get matching dirs named 'test.<something>'
    for (_,dirs,_) in os.walk(TestPath):
        test_dirs = [ x for x in dirs if x.startswith('exception.test.') ]
        break # First level of walk is enough.

    for subdir in test_dirs:
        print(f"Running negative (exception) test in {subdir}.")
        path = os.path.join(TestPath, subdir)

        # This succeeds *IF* the exception is raised, otherwise fails
        with pytest.raises(dacite.UnexpectedDataError) as ee:
            ast_root = vsc_parser.get_ast_from_file(os.path.join(path, 'input.yaml'))

# Unused
default_templates = {}

# TODO: Loop over subdirectories in tests to perform tests for different
# 'input.yaml/template/result' files
