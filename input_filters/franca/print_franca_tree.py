# vim: tw=120 ts=4 et
# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project

"""This is a quick-and dirty tree (YAML) printer for the Franca AST from the franca parser, used for debugging only."""

# Have to define a search path to submodule to make this work (might be rearranged later)
import os
import sys
mydir = os.path.dirname(__file__)
for p in ['pyfranca', 'pyfranca/pyfranca']:
    if p not in sys.path:
        sys.path.append(os.path.join(mydir,p))

import oyaml
import input_filters.franca.pyfranca.pyfranca as pyfranca
from collections import OrderedDict

def is_simple_type(t) -> bool:
    return t.__class__.__module__ == 'builtins'

def franca_ast_to_dict(node, debug_context="") -> OrderedDict:

    """Given a root node, return a key-value mapping dict (which represents the YAML equivalent, so we can print it as
    a YAML tree for viewing. The function is recursive. """

    if node is None:
        raise TypeError(f"None-value should not be passed to function, parent debug: {debug_context=}")

    # Strings/ints/etc are directly understood by the YAML output printer so just put them in.
    if type(node).__class__.__module__ == 'builtins':
        return node

    # In addition to dicts, we might have python lists, which will be output as lists in YAML
    if type(node) is list:
        ret = []
        for listitem in node:
            ret.append(franca_ast_to_dict(listitem, debug_context=str(node)))
        return ret

    if type(node) is OrderedDict:
        ret = []
        for listitem in node.items():
            ret.append(franca_ast_to_dict(listitem, debug_context=str(node)))
        return ret

    # New dict containing all key-value pairs at this level
    ret = OrderedDict()

    try:
        _fields = fields(node)
    except:
        print(f"Error occurred processing fields for {node=}")
        _fields = []

    for f in _fields:
        item = getattr(node, f.name)
        if not is_empty(item):
            ret[f.name] = ifex_ast_to_dict(item, debug_context=str(f))

    return ret


def parse_franca(fidl_file):
    processor = pyfranca.Processor()
    return processor.import_file(fidl_file)  # This returns the top level package


# --- Script entry point ---

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print(f"Usage: python {os.path.basename(__file__)} <filename>")
        sys.exit(3)

    print(oyaml.dump(franca_ast_to_dict(parse_franca(sys.argv[1]))))
