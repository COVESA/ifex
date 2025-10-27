# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

"""
Tests for the AIDL output filter.

Covers:
  1. AIDL AST model construction
  2. IFEX → AIDL transformation (unit test on AST structure)
  3. AIDL → text rendering (checks generated .aidl syntax)
  4. Entrypoint smoke test
"""

import os
import sys
import pytest

from ifex.models.ifex.ifex_parser import get_ast_from_yaml_file
from ifex.output_filters.aidl.ifex_to_aidl import ifex_to_aidl, translate_type
from ifex.output_filters.aidl.aidl_generator import aidl_file_to_text, aidl_to_text
from ifex.models.aidl.aidl_ast import (
    AIDLFile, Interface, Parcelable, Enum, Method, Parameter, ParcelableField, EnumElement
)

TEST_DIR   = os.path.dirname(os.path.realpath(__file__))
SAMPLE_IFEX = os.path.join(TEST_DIR, "test.aidl.sample", "input.yaml")


# ---------------------------------------------------------------------------
# 1. Type translation
# ---------------------------------------------------------------------------

def test_translate_type_primitives():
    assert translate_type("int32")   == "int"
    assert translate_type("int64")   == "long"
    assert translate_type("float")   == "float"
    assert translate_type("double")  == "double"
    assert translate_type("boolean") == "boolean"
    assert translate_type("string")  == "String"
    assert translate_type("uint8")   == "byte"
    assert translate_type("int16")   == "short"

def test_translate_type_array():
    assert translate_type("int32[]") == "int[]"
    assert translate_type("string[]") == "String[]"

def test_translate_type_unknown_passthrough():
    assert translate_type("MyCustomType") == "MyCustomType"


# ---------------------------------------------------------------------------
# 2. IFEX → AIDL AST transformation
# ---------------------------------------------------------------------------

def test_ifex_to_aidl_produces_three_files():
    ast = get_ast_from_yaml_file(SAMPLE_IFEX)
    files = ifex_to_aidl(ast)
    # expect: IClimateControl.aidl, ClimateZone.aidl, AirflowMode.aidl
    assert len(files) == 3

def test_ifex_to_aidl_interface_file():
    ast = get_ast_from_yaml_file(SAMPLE_IFEX)
    files = ifex_to_aidl(ast)
    iface_file = next(f for f in files if isinstance(f.declaration, Interface))
    iface = iface_file.declaration
    assert iface.name == "IClimateControl"
    assert iface_file.package == "com.example.vehicle"

def test_ifex_to_aidl_interface_methods():
    ast = get_ast_from_yaml_file(SAMPLE_IFEX)
    files = ifex_to_aidl(ast)
    iface = next(f.declaration for f in files if isinstance(f.declaration, Interface))
    method_names = [m.name for m in iface.methods]
    assert "setTemperature" in method_names
    assert "getTemperature" in method_names
    assert "onTemperatureChanged" in method_names

def test_ifex_to_aidl_method_return_type():
    ast = get_ast_from_yaml_file(SAMPLE_IFEX)
    files = ifex_to_aidl(ast)
    iface = next(f.declaration for f in files if isinstance(f.declaration, Interface))
    get_temp = next(m for m in iface.methods if m.name == "getTemperature")
    assert get_temp.return_type == "float"

def test_ifex_to_aidl_method_void_return():
    ast = get_ast_from_yaml_file(SAMPLE_IFEX)
    files = ifex_to_aidl(ast)
    iface = next(f.declaration for f in files if isinstance(f.declaration, Interface))
    set_temp = next(m for m in iface.methods if m.name == "setTemperature")
    assert set_temp.return_type == "void"

def test_ifex_to_aidl_event_is_oneway():
    ast = get_ast_from_yaml_file(SAMPLE_IFEX)
    files = ifex_to_aidl(ast)
    iface = next(f.declaration for f in files if isinstance(f.declaration, Interface))
    event_method = next(m for m in iface.methods if m.name == "onTemperatureChanged")
    assert event_method.oneway is True
    assert event_method.return_type == "void"

def test_ifex_to_aidl_parameter_directions():
    ast = get_ast_from_yaml_file(SAMPLE_IFEX)
    files = ifex_to_aidl(ast)
    iface = next(f.declaration for f in files if isinstance(f.declaration, Interface))
    set_temp = next(m for m in iface.methods if m.name == "setTemperature")
    param_names = {p.name: p.direction for p in set_temp.parameters}
    assert param_names["zone"]        == "in"
    assert param_names["temperature"] == "in"
    assert param_names["success"]     == "out"

def test_ifex_to_aidl_parcelable():
    ast = get_ast_from_yaml_file(SAMPLE_IFEX)
    files = ifex_to_aidl(ast)
    parcelable_file = next(f for f in files if isinstance(f.declaration, Parcelable))
    p = parcelable_file.declaration
    assert p.name == "ClimateZone"
    field_names = [f.name for f in p.fields]
    assert "zoneId"     in field_names
    assert "targetTemp" in field_names
    assert "active"     in field_names

def test_ifex_to_aidl_enum():
    ast = get_ast_from_yaml_file(SAMPLE_IFEX)
    files = ifex_to_aidl(ast)
    enum_file = next(f for f in files if isinstance(f.declaration, Enum))
    e = enum_file.declaration
    assert e.name == "AirflowMode"
    element_names = [el.name for el in e.elements]
    assert "AUTO"     in element_names
    assert "MANUAL"   in element_names
    assert "MAX_COOL" in element_names


# ---------------------------------------------------------------------------
# 3. AIDL → text rendering
# ---------------------------------------------------------------------------

def test_aidl_interface_text():
    ast = get_ast_from_yaml_file(SAMPLE_IFEX)
    files = ifex_to_aidl(ast)
    iface_file = next(f for f in files if isinstance(f.declaration, Interface))
    text = aidl_file_to_text(iface_file)
    assert "package com.example.vehicle;" in text
    assert "interface IClimateControl {" in text
    assert "getTemperature" in text
    assert "oneway" in text         # for the event method

def test_aidl_parcelable_text():
    ast = get_ast_from_yaml_file(SAMPLE_IFEX)
    files = ifex_to_aidl(ast)
    parcelable_file = next(f for f in files if isinstance(f.declaration, Parcelable))
    text = aidl_file_to_text(parcelable_file)
    assert "parcelable ClimateZone {" in text
    assert "int zoneId;" in text
    assert "float targetTemp;" in text

def test_aidl_enum_text():
    ast = get_ast_from_yaml_file(SAMPLE_IFEX)
    files = ifex_to_aidl(ast)
    enum_file = next(f for f in files if isinstance(f.declaration, Enum))
    text = aidl_file_to_text(enum_file)
    assert "enum AirflowMode {" in text
    assert "AUTO" in text
    assert "MANUAL" in text

def test_aidl_method_in_out_params_text():
    ast = get_ast_from_yaml_file(SAMPLE_IFEX)
    files = ifex_to_aidl(ast)
    iface_file = next(f for f in files if isinstance(f.declaration, Interface))
    text = aidl_file_to_text(iface_file)
    assert "in int zone" in text
    assert "out boolean success" in text

def test_aidl_combined_output():
    ast = get_ast_from_yaml_file(SAMPLE_IFEX)
    files = ifex_to_aidl(ast)
    text = aidl_to_text(files)
    assert "IClimateControl.aidl" in text
    assert "ClimateZone.aidl"     in text
    assert "AirflowMode.aidl"     in text


# ---------------------------------------------------------------------------
# 4. Entrypoint smoke test
# ---------------------------------------------------------------------------

def test_ifex_to_aidl_entrypoint(monkeypatch, capsys):
    from distribution.entrypoints.ifex_to_aidl import ifex_to_aidl_run
    monkeypatch.setattr(sys, "argv", ["ifex_to_aidl", SAMPLE_IFEX])
    ifex_to_aidl_run()
    output = capsys.readouterr().out
    assert "ERROR" not in output
    assert "interface IClimateControl" in output
    assert "parcelable ClimateZone" in output
    assert "enum AirflowMode" in output
