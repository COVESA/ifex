# SPDX-FileCopyrightText: Copyright (c) 2025 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

import argparse
import os
import sys
from models.protobuf import protobuf_ast, protobuf_lark
from output_filters import JinjaSetup
from input_filters.protobuf import protobuf_to_ifex

def gen_str_or_int(item):
    if item.isdigit():
        return int(item)  # Could also be just item... either way jinja should output just the number
    else:
        return '"' + item + '"'  # Quoted string


def ast_to_text(proto_ast: protobuf_ast.Proto) -> str:
    # Set up Jinja environment - collect templates that match the names of the
    # Proto AST classes (recursive search through AST types).
    jinja_setup = JinjaSetup.JinjaTemplateEnv(protobuf_ast.Proto, template_dir)

    # Reuse the protobuf-parser function in protobuf_to_ifex
    path = os.path.dirname(protobuf_to_ifex.__file__)

    # Get a handle to the gen() function
    gen = jinja_setup.create_gen_closure()

    # Import the gen() function to Jinja environment
    jinja_setup.set_template_env(gen=gen, gen_str_or_int=gen_str_or_int)

    # Call Jinja generation with the top node.  Templates take care of the
    # subsequent recursive calls for all found member variables in the nodes
    return gen(proto_ast)


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

    # Parse the given input file (gRPC/proto format expected)
    proto_ast = protobuf_lark.get_ast_from_proto_file(args.protofile)

    # Print out the AST as text
    print(ast_to_text(proto_ast))

