# SPDX-FileCopyrightText: Copyright (c) 2025 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

import argparse
import os
import sys
from models.protobuf import protobuf_ast
from output_filters import JinjaSetup
from input_filters.protobuf import protobuf_to_ifex

# This parses a Protobuf/gRPC file and then prints it back out again.  
# Text -> Protobuf Parser -> Protobuf AST -> to text via Jinja templates
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.description = """
        gRPC/protobuf round-trip for testing.
        Parse a gRPC file into our AST format, then print it out again, using our generator.
        """

    parser.add_argument("protofile", help="Input file.", nargs="?")
    args = parser.parse_args()

    if args.protofile is None:
        parser.print_help()
        sys.exit(1)

    # Get template directory which is templates/ relative to this file location
    template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")

    # Set up Jinja environment - collect templates that match the names of the
    # Proto AST classes (recursive search through AST types).
    jinja_setup = JinjaSetup.JinjaTemplateEnv(protobuf_ast.Proto, template_dir)

    # Reuse the protobuf-parser function in protobuf_to_ifex
    path = os.path.dirname(protobuf_to_ifex.__file__)

    # Parse the given input file (gRPC/proto format expected)
    proto_ast = protobuf_to_ifex.proto_ast_from_input(args.protofile)

    # Get a handle to the gen() function
    gen = jinja_setup.create_gen_closure()

    # Import the gen() function to Jinja environment
    jinja_setup.set_template_env(gen=gen)

    # And call Jinja generation with the top node.  Templates take care of the
    # subsequent recursive calls for all found member variables in the nodes
    print(gen(proto_ast))
