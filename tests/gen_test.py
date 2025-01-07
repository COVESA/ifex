# SPDX-License-Identifier: MPL-2.0
# ----------------------------------------------------------------------------
# (C) 2021 COVESA
# Test code for code generator part of IFEX
# ----------------------------------------------------------------------------
# This is maybe not ideal way but seems efficient enough
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

import yaml

from models.ifex import ifex_ast, ifex_parser, ifex_generator
import models.ifex.ifex_ast_introspect as introspect
import dacite, pytest
import os

from models.ifex.ifex_ast import Argument, AST, Namespace, Interface, Method
from models.ifex.ifex_ast_construction import ifex_ast_as_yaml

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
        ast_root = ifex_parser.get_ast_from_yaml_file(os.path.join(path, 'input.yaml'))

        with open(os.path.join(path,"template"), "r") as template_file:
            generated = ifex_generator.gen_template_text(ast_root, template_file.read())

        with open(os.path.join(path,"result"), "r") as result_file:
            # Apparently we must strip newline or it will be added superfluously here
            # even if it is not in the file. The same does not happen on the
            # jinja-template generation we are comparing to.
            wanted = result_file.read().rstrip()
            assert generated == wanted


def test_ast_gen():
    service = ifex_parser.get_ast_from_yaml_file(os.path.join(TestPath, 'test.sample', 'input.yaml'))

    assert service.name == "named_service"
    assert service.major_version == 3
    assert service.minor_version == 0


# This does not assert anything -> but if printouts are captured they can be studied
def test_print():
    ast = ifex_parser.get_ast_from_yaml_file(os.path.join(TestPath, 'test.variant', 'input.yaml'))
    print(yaml.dump(ast, sort_keys=False))
    print(introspect.get_variant_types(ast.namespaces[0].typedefs[0]))

# Test expectations and helper-functions on the variant type
def test_variant():
    ast = ifex_parser.get_ast_from_yaml_file(os.path.join(TestPath, 'test.variant', 'input.yaml'))
    # Method argument
    v0type = ast.namespaces[0].methods[0].input[0].datatype
    assert not introspect.is_ifex_variant_typedef(v0type)
    assert introspect.is_ifex_variant_shortform(v0type)

    # Typdefs
    v1 = ast.namespaces[0].typedefs[0]
    v2 = ast.namespaces[0].typedefs[1]
    assert introspect.is_ifex_variant_typedef(v1)
    assert introspect.is_ifex_variant_typedef(v2)
    assert introspect.is_ifex_variant_shortform(v2.datatype)


def test_ast_manual():
    service = ifex_ast.AST(name='test', description='test', major_version=1, minor_version=0)

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
            ast_root = ifex_parser.get_ast_from_yaml_file(os.path.join(path, 'input.yaml'))

@dataclass
class Argument(Argument):
    name: str
    simple_type_str: Optional[str] = None
    simple_type_int: Optional[int] = None
    simple_type_bool: Optional[bool] = None
    simple_type_float: Optional[float] = None
    simple_type_date: Optional[date] = None
    simple_type_datetime: Optional[datetime] = None


def test_simple_types():
    simple_types = yaml.safe_load(ifex_ast_as_yaml(AST(namespaces=[
        Namespace(
            name="namespace1",
            interface=Interface(
                name="interface1",
                methods=[
                    Method(
                        name="method1",
                        input=[
                            Argument(
                                name="argument1",
                                datatype="mixed",
                                simple_type_str="string",
                                simple_type_int=123,
                                simple_type_bool=True,
                                simple_type_float=123.45,
                                simple_type_date=date.today(),
                                simple_type_datetime=datetime.now()
                            )
                        ]
                    )
                ]
            )
        )
    ])))["namespaces"][0]["interface"]["methods"][0]["input"][0]

    assert type(simple_types["simple_type_str"]) == str
    assert type(simple_types["simple_type_int"]) == int
    assert type(simple_types["simple_type_bool"]) == bool
    assert type(simple_types["simple_type_float"]) == float
    assert type(simple_types["simple_type_date"]) == date
    assert type(simple_types["simple_type_datetime"]) == datetime


# Unused
default_templates = {}

# TODO: Loop over subdirectories in tests to perform tests for different
# 'input.yaml/template/result' files