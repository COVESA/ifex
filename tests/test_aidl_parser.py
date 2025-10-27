# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# Comprehensive tests of the AIDL parser.  These are mostly AI-generated and
# have only moderate value for proving the parser, but since they cover a lot
# of different features they are likely to at least pick up regressions.

# FIXME These are also quite inefficient because they will re-parse the same
# input file for each small test (but the files are small also)

import os
import sys
import pytest

from ifex.models.aidl.aidl_lark import get_ast_from_aidl_file, parse_text
from ifex.models.aidl.aidl_ast import (
    AIDLFile, Interface, Parcelable, Enum,
    Method, Parameter, ParcelableField, EnumElement, Const,
)
from ifex.input_filters.aidl.aidl_to_ifex import aidl_to_ifex
import ifex.models.ifex.ifex_ast as ifex_ast

TEST_DIR    = os.path.dirname(os.path.realpath(__file__))
SAMPLE_DIR  = os.path.join(TEST_DIR, "test.aidl.sample")

IFACE_FILE  = os.path.join(SAMPLE_DIR, "IClimateControl.aidl")
PARCEL_FILE = os.path.join(SAMPLE_DIR, "ClimateZone.aidl")
ENUM_FILE   = os.path.join(SAMPLE_DIR, "AirflowMode.aidl")


# ---------------------------------------------------------------------------
# 1. Grammar / parser — interface
# ---------------------------------------------------------------------------

def test_parse_interface_returns_aidl_file():
    result = get_ast_from_aidl_file(IFACE_FILE)
    assert isinstance(result, AIDLFile)

def test_parse_interface_package():
    result = get_ast_from_aidl_file(IFACE_FILE)
    assert result.package == "com.example.vehicle"

def test_parse_interface_declaration_type():
    result = get_ast_from_aidl_file(IFACE_FILE)
    assert isinstance(result.declaration, Interface)

def test_parse_interface_name():
    result = get_ast_from_aidl_file(IFACE_FILE)
    assert result.declaration.name == "IClimateControl"

def test_parse_interface_method_count():
    result = get_ast_from_aidl_file(IFACE_FILE)
    assert len(result.declaration.methods) == 3

def test_parse_interface_method_names():
    result = get_ast_from_aidl_file(IFACE_FILE)
    names = [m.name for m in result.declaration.methods]
    assert "setTemperature"    in names
    assert "getTemperature"    in names
    assert "onTemperatureChanged" in names

def test_parse_interface_oneway_method():
    result = get_ast_from_aidl_file(IFACE_FILE)
    event = next(m for m in result.declaration.methods if m.name == "onTemperatureChanged")
    assert event.oneway is True
    assert event.return_type == "void"

def test_parse_interface_non_oneway_method():
    result = get_ast_from_aidl_file(IFACE_FILE)
    method = next(m for m in result.declaration.methods if m.name == "setTemperature")
    assert method.oneway is False

def test_parse_interface_return_type():
    result = get_ast_from_aidl_file(IFACE_FILE)
    get_temp = next(m for m in result.declaration.methods if m.name == "getTemperature")
    assert get_temp.return_type == "float"

def test_parse_interface_void_return():
    result = get_ast_from_aidl_file(IFACE_FILE)
    set_temp = next(m for m in result.declaration.methods if m.name == "setTemperature")
    assert set_temp.return_type == "void"

def test_parse_interface_parameter_count():
    result = get_ast_from_aidl_file(IFACE_FILE)
    set_temp = next(m for m in result.declaration.methods if m.name == "setTemperature")
    assert len(set_temp.parameters) == 3

def test_parse_interface_parameter_directions():
    result = get_ast_from_aidl_file(IFACE_FILE)
    set_temp = next(m for m in result.declaration.methods if m.name == "setTemperature")
    directions = {p.name: p.direction for p in set_temp.parameters}
    assert directions["zone"]        == "in"
    assert directions["temperature"] == "in"
    assert directions["success"]     == "out"

def test_parse_interface_parameter_types():
    result = get_ast_from_aidl_file(IFACE_FILE)
    set_temp = next(m for m in result.declaration.methods if m.name == "setTemperature")
    types = {p.name: p.datatype for p in set_temp.parameters}
    assert types["zone"]        == "int"
    assert types["temperature"] == "float"
    assert types["success"]     == "boolean"


# ---------------------------------------------------------------------------
# 2. Grammar / parser — parcelable
# ---------------------------------------------------------------------------

def test_parse_parcelable_returns_aidl_file():
    result = get_ast_from_aidl_file(PARCEL_FILE)
    assert isinstance(result, AIDLFile)

def test_parse_parcelable_package():
    result = get_ast_from_aidl_file(PARCEL_FILE)
    assert result.package == "com.example.vehicle"

def test_parse_parcelable_declaration_type():
    result = get_ast_from_aidl_file(PARCEL_FILE)
    assert isinstance(result.declaration, Parcelable)

def test_parse_parcelable_name():
    result = get_ast_from_aidl_file(PARCEL_FILE)
    assert result.declaration.name == "ClimateZone"

def test_parse_parcelable_field_count():
    result = get_ast_from_aidl_file(PARCEL_FILE)
    assert len(result.declaration.fields) == 3

def test_parse_parcelable_field_names():
    result = get_ast_from_aidl_file(PARCEL_FILE)
    names = [f.name for f in result.declaration.fields]
    assert "zoneId"     in names
    assert "targetTemp" in names
    assert "active"     in names

def test_parse_parcelable_field_types():
    result = get_ast_from_aidl_file(PARCEL_FILE)
    types = {f.name: f.datatype for f in result.declaration.fields}
    assert types["zoneId"]     == "int"
    assert types["targetTemp"] == "float"
    assert types["active"]     == "boolean"


# ---------------------------------------------------------------------------
# 3. Grammar / parser — enum
# ---------------------------------------------------------------------------

def test_parse_enum_returns_aidl_file():
    result = get_ast_from_aidl_file(ENUM_FILE)
    assert isinstance(result, AIDLFile)

def test_parse_enum_package():
    result = get_ast_from_aidl_file(ENUM_FILE)
    assert result.package == "com.example.vehicle"

def test_parse_enum_declaration_type():
    result = get_ast_from_aidl_file(ENUM_FILE)
    assert isinstance(result.declaration, Enum)

def test_parse_enum_name():
    result = get_ast_from_aidl_file(ENUM_FILE)
    assert result.declaration.name == "AirflowMode"

def test_parse_enum_element_count():
    result = get_ast_from_aidl_file(ENUM_FILE)
    assert len(result.declaration.elements) == 3

def test_parse_enum_element_names():
    result = get_ast_from_aidl_file(ENUM_FILE)
    names = [e.name for e in result.declaration.elements]
    assert "AUTO"     in names
    assert "MANUAL"   in names
    assert "MAX_COOL" in names

def test_parse_enum_element_values():
    result = get_ast_from_aidl_file(ENUM_FILE)
    vals = {e.name: e.value for e in result.declaration.elements}
    assert vals["AUTO"]     == "0"
    assert vals["MANUAL"]   == "1"
    assert vals["MAX_COOL"] == "2"


# ---------------------------------------------------------------------------
# 4. parse_text — inline text parsing
# ---------------------------------------------------------------------------

def test_parse_text_minimal_interface():
    src = """
package com.test;
interface IFoo {
    void doSomething(in int x);
}
"""
    result = parse_text(src)
    assert isinstance(result.declaration, Interface)
    assert result.declaration.name == "IFoo"
    assert result.package == "com.test"
    assert result.declaration.oneway == False

def test_parse_text_minimal_parcelable():
    src = """
package com.test;
parcelable Bar {
    String name;
}
"""
    result = parse_text(src)
    assert isinstance(result.declaration, Parcelable)
    assert result.declaration.name == "Bar"
    assert result.declaration.fields[0].name == "name"
    assert result.declaration.fields[0].datatype == "String"

def test_parse_text_minimal_enum():
    src = """
package com.test;
enum Status {
    OK = 0,
    ERR = 1,
}
"""
    result = parse_text(src)
    assert isinstance(result.declaration, Enum)
    assert result.declaration.name == "Status"
    assert len(result.declaration.elements) == 2

def test_parse_text_with_import():
    src = """
package com.test;
import com.other.Baz;
interface IFoo {
    void run();
}
"""
    result = parse_text(src)
    assert result.imports is not None
    assert len(result.imports) == 1
    assert result.imports[0].path == "com.other.Baz"

def test_parse_text_const_in_interface():
    src = """
package com.test;
interface IFoo {
    const int MAX_RETRIES = 3;
    void retry();
}
"""
    result = parse_text(src)
    iface = result.declaration
    assert iface.consts is not None
    assert iface.consts[0].name == "MAX_RETRIES"
    assert iface.consts[0].datatype == "int"
    assert iface.consts[0].value == "3"

def test_parse_text_comment_stripping():
    src = """
/* File header comment */
package com.test; // inline comment
interface IBar { // another comment
    // method comment
    void run();
}
"""
    result = parse_text(src)
    assert result.declaration.name == "IBar"

def test_parse_text_array_type():
    src = """
package com.test;
parcelable DataBlob {
    byte[] data;
}
"""
    result = parse_text(src)
    assert result.declaration.fields[0].datatype == "byte[]"

def test_parse_text_inout_param():
    src = """
package com.test;
interface IFoo {
    void process(inout int value);
}
"""
    result = parse_text(src)
    param = result.declaration.methods[0].parameters[0]
    assert param.direction == "inout"
    assert param.name == "value"

def test_parse_text_enum_no_values():
    src = """
package com.test;
enum Color {
    RED,
    GREEN,
    BLUE,
}
"""
    result = parse_text(src)
    assert isinstance(result.declaration, Enum)
    names = [e.name for e in result.declaration.elements]
    assert names == ["RED", "GREEN", "BLUE"]
    # Values should all be None since no = assignment
    for e in result.declaration.elements:
        assert e.value is None

def test_parse_text_oneway_interface():
    src = """
package com.test;
oneway interface INotifier {
    void notify(in int code);
}
"""
    result = parse_text(src)
    iface = result.declaration
    assert iface.oneway is True


# ---------------------------------------------------------------------------
# 5. AIDL → IFEX conversion
# ---------------------------------------------------------------------------

def test_aidl_to_ifex_interface_namespace():
    aidl = get_ast_from_aidl_file(IFACE_FILE)
    result = aidl_to_ifex(aidl)
    assert len(result.namespaces) == 1
    assert result.namespaces[0].name == "com.example.vehicle"

def test_aidl_to_ifex_interface_name():
    aidl = get_ast_from_aidl_file(IFACE_FILE)
    result = aidl_to_ifex(aidl)
    ns = result.namespaces[0]
    assert ns.interface is not None
    assert ns.interface.name == "ClimateControl"   # "I" prefix stripped

def test_aidl_to_ifex_interface_methods():
    aidl = get_ast_from_aidl_file(IFACE_FILE)
    result = aidl_to_ifex(aidl)
    iface = result.namespaces[0].interface
    method_names = [m.name for m in (iface.methods or [])]
    assert "setTemperature" in method_names
    assert "getTemperature" in method_names

def test_aidl_to_ifex_event():
    aidl = get_ast_from_aidl_file(IFACE_FILE)
    result = aidl_to_ifex(aidl)
    iface = result.namespaces[0].interface
    event_names = [e.name for e in (iface.events or [])]
    assert "onTemperatureChanged" in event_names

def test_aidl_to_ifex_method_input_output():
    aidl = get_ast_from_aidl_file(IFACE_FILE)
    result = aidl_to_ifex(aidl)
    iface = result.namespaces[0].interface
    set_temp = next(m for m in iface.methods if m.name == "setTemperature")
    input_names  = [a.name for a in (set_temp.input  or [])]
    output_names = [a.name for a in (set_temp.output or [])]
    assert "zone"        in input_names
    assert "temperature" in input_names
    assert "success"     in output_names

def test_aidl_to_ifex_method_returns():
    aidl = get_ast_from_aidl_file(IFACE_FILE)
    result = aidl_to_ifex(aidl)
    iface = result.namespaces[0].interface
    get_temp = next(m for m in iface.methods if m.name == "getTemperature")
    assert get_temp.returns is not None
    assert get_temp.returns[0].datatype == "float"

def test_aidl_to_ifex_parcelable_struct():
    aidl = get_ast_from_aidl_file(PARCEL_FILE)
    result = aidl_to_ifex(aidl)
    ns = result.namespaces[0]
    assert ns.structs is not None
    assert ns.structs[0].name == "ClimateZone"

def test_aidl_to_ifex_parcelable_members():
    aidl = get_ast_from_aidl_file(PARCEL_FILE)
    result = aidl_to_ifex(aidl)
    struct = result.namespaces[0].structs[0]
    member_names = [m.name for m in (struct.members or [])]
    assert "zoneId"     in member_names
    assert "targetTemp" in member_names
    assert "active"     in member_names

def test_aidl_to_ifex_parcelable_member_types():
    aidl = get_ast_from_aidl_file(PARCEL_FILE)
    result = aidl_to_ifex(aidl)
    struct = result.namespaces[0].structs[0]
    types = {m.name: m.datatype for m in (struct.members or [])}
    assert types["zoneId"]     == "int32"
    assert types["targetTemp"] == "float"
    assert types["active"]     == "boolean"

def test_aidl_to_ifex_enum():
    aidl = get_ast_from_aidl_file(ENUM_FILE)
    result = aidl_to_ifex(aidl)
    ns = result.namespaces[0]
    assert ns.enumerations is not None
    assert ns.enumerations[0].name == "AirflowMode"

def test_aidl_to_ifex_enum_datatype():
    aidl = get_ast_from_aidl_file(ENUM_FILE)
    result = aidl_to_ifex(aidl)
    enum = result.namespaces[0].enumerations[0]
    assert enum.datatype == "int32"

def test_aidl_to_ifex_enum_options():
    aidl = get_ast_from_aidl_file(ENUM_FILE)
    result = aidl_to_ifex(aidl)
    enum = result.namespaces[0].enumerations[0]
    option_names = [o.name for o in (enum.options or [])]
    assert "AUTO"     in option_names
    assert "MANUAL"   in option_names
    assert "MAX_COOL" in option_names

def test_aidl_to_ifex_type_translation():
    src = """
package com.test;
parcelable Types {
    int    a;
    long   b;
    float  c;
    double d;
    boolean e;
    String  f;
    byte    g;
    short   h;
}
"""
    aidl = parse_text(src)
    result = aidl_to_ifex(aidl)
    struct = result.namespaces[0].structs[0]
    types = {m.name: m.datatype for m in struct.members}
    assert types["a"] == "int32"
    assert types["b"] == "int64"
    assert types["c"] == "float"
    assert types["d"] == "double"
    assert types["e"] == "boolean"
    assert types["f"] == "string"
    assert types["g"] == "uint8"
    assert types["h"] == "int16"


# ---------------------------------------------------------------------------
# 6. Entrypoint smoke test
# ---------------------------------------------------------------------------

def test_aidl_to_ifex_entrypoint(monkeypatch, capsys):
    from distribution.entrypoints.aidl_to_ifex import aidl_to_ifex_run
    monkeypatch.setattr(sys, "argv", ["aidl_to_ifex", IFACE_FILE])
    aidl_to_ifex_run()
    output = capsys.readouterr().out
    assert "ERROR" not in output
    assert "ClimateControl" in output  # interface name (I prefix stripped)
    assert "com.example.vehicle" in output

def test_aidl_to_ifex_entrypoint_parcelable(monkeypatch, capsys):
    from distribution.entrypoints.aidl_to_ifex import aidl_to_ifex_run
    monkeypatch.setattr(sys, "argv", ["aidl_to_ifex", PARCEL_FILE])
    aidl_to_ifex_run()
    output = capsys.readouterr().out
    assert "ERROR" not in output
    assert "ClimateZone" in output

def test_aidl_to_ifex_entrypoint_enum(monkeypatch, capsys):
    from distribution.entrypoints.aidl_to_ifex import aidl_to_ifex_run
    monkeypatch.setattr(sys, "argv", ["aidl_to_ifex", ENUM_FILE])
    aidl_to_ifex_run()
    output = capsys.readouterr().out
    assert "ERROR" not in output
    assert "AirflowMode" in output
