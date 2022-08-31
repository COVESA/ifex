# SPDX-License-Identifier: MPL-2.0
# ----------------------------------------------------------------------------
# (C) 2021 COVESA
# Reader/parser module
# To be used by all generators and other tools
# ----------------------------------------------------------------------------

"""
VSC parser/reader to be used by generators and other tools
"""

# This is now a small wrapper around vsc_ast.py
# In fact, it seems likely that this file should be removed since it has
# almost no function left.

from vsc.model import vsc_ast

def get_ast_from_file(filepath : str):
    return vsc_ast.read_ast_from_yaml_file(filepath)

