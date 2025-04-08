# SPDX-License-Identifier: MPL-2.0
# ----------------------------------------------------------------------------
# (C) 2021 COVESA
# Test code for code generator part of IFEX -> modified to run protobuf tests
# ----------------------------------------------------------------------------

from models.protobuf import protobuf_lark as protobuf_parser
from output_filters.grpc import grpc_generator
import os

TestPath = os.path.dirname(os.path.realpath(__file__))

def test_gen():

    # Get matching dirs named 'test.<something>'
    for (_,dirs,_) in os.walk(TestPath):
        test_dirs = [ x for x in dirs if x.startswith('test.proto.') ]
        break # First level of walk is enough.

    for subdir in test_dirs:
        print(f"Running test in {subdir}.")
        path = os.path.join(TestPath, subdir)

        # The files named 'input.yaml', 'template' and 'result' are in each test directory
        ast_root = protobuf_parser.get_ast_from_proto_file(os.path.join(path, 'input'))

        template_dir = os.path.join(os.path.dirname(grpc_generator.__file__), "templates")

        generated = grpc_generator.ast_to_text(ast_root, template_dir)

        with open(os.path.join(path,"result"), "r") as result_file:
            # Apparently we must strip newline or it will be added superfluously here
            # even if it is not in the file. The same does not happen on the
            # jinja-template generation we are comparing to.
            wanted = result_file.read()
            assert generated == wanted


if __name__ == '__main__':
    test_gen()

