# SPDX-License-Identifier: MPL-2.0
# ----------------------------------------------------------------------------
# (C) 2025 MBition GmbH
# Test code for merge-tree functions
# ----------------------------------------------------------------------------
# vim: sw=4 et

from models.ifex.ifex_ast import *
from models.ifex.ifex_ast_construction import ifex_ast_as_yaml
from models.ifex.ifex_parser import get_ast_from_yaml_file
from transformers.merge_overlay import *
import difflib
import os
import sys

# HELPERS

TestPath = os.path.dirname(os.path.realpath(__file__))
merge_test_dir = os.path.join(TestPath, 'merge_tree')

def merge(f1, f2):
    file1 = os.path.join(merge_test_dir, f1)
    file2 = os.path.join(merge_test_dir, f2)
    ast1 = get_ast_from_yaml_file(file1)
    ast2 = get_ast_from_yaml_file(file2)
    merged_ast = merge_asts(ast1, ast2)
    return ifex_ast_as_yaml(merged_ast)

def compare(f1, f2, resultfile):
    generated = merge(f1,f2).splitlines(keepends=True)

    compare_file = os.path.join(merge_test_dir, resultfile)
    with open(compare_file, "r") as result_file:
        wanted = result_file.readlines()
        if generated != wanted:
            diff = difflib.unified_diff(generated, wanted, fromfile="generated", tofile=resultfile)
            
            # diff is a generator - need to iterate over it and print
            sys.stdout.writelines(diff)

        assert generated == wanted

# PYTEST ACTUAL TESTS:

def test_merge1():
    compare("one", "two", "one+two")

def test_merge2():
    compare("one", "three", "one+three")

def test_merge3():
    compare("four", "five", "four+five")

if __name__ == '__main__':
    test_merge1()
    test_merge2()
    test_merge3()

