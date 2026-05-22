# SPDX-License-Identifier: MPL-2.0

"""Tests that a dot-separated namespace name expands to the same AST as
explicitly nested namespaces."""

from pathlib import Path
from ifex.models.ifex.ifex_parser import get_ast_from_yaml_file
from ifex.models.ifex.ifex_ast import Namespace

HERE = Path(__file__).resolve().parent


def _names(ns: Namespace) -> list:
    """Return a nested list of namespace names mirroring the tree structure."""
    return [ns.name, [_names(child) for child in ns.namespaces]]


def test_dot_path_expands_to_nested():
    dot = get_ast_from_yaml_file(str(HERE / "dotpath.ifex"))
    nested = get_ast_from_yaml_file(str(HERE / "nested.ifex"))

    # Both should produce exactly one top-level namespace: com
    assert len(dot.namespaces) == 1
    assert len(nested.namespaces) == 1

    # The namespace tree shapes must match
    assert _names(dot.namespaces[0]) == _names(nested.namespaces[0])

    # The innermost namespace (vehicle) must carry the method
    dot_vehicle = dot.namespaces[0].namespaces[0].namespaces[0]
    assert dot_vehicle.name == "vehicle"
    assert dot_vehicle.description == "Vehicle namespace"
    assert len(dot_vehicle.methods) == 1
    assert dot_vehicle.methods[0].name == "start"


def test_plain_namespace_name_unchanged():
    """A namespace without dots must not be modified."""
    nested = get_ast_from_yaml_file(str(HERE / "nested.ifex"))
    assert nested.namespaces[0].name == "com"


def test_partial_dot_path():
    """A two-part dot path produces exactly two namespace levels."""
    from ifex.models.ifex.ifex_parser import _expand_dot_namespace
    from ifex.models.ifex.ifex_ast import Namespace, Method

    ns = Namespace(name="A.B", methods=[Method(name="foo")])
    expanded = _expand_dot_namespace(ns)

    assert expanded.name == "A"
    assert len(expanded.namespaces) == 1
    assert expanded.namespaces[0].name == "B"
    assert expanded.namespaces[0].methods[0].name == "foo"
