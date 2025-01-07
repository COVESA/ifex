# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# User-invocation script for protobuf-to-ifex

from other.protobuf import protobuf_to_ifex
import argparse

def protobuf_to_ifex_run():

    parser = argparse.ArgumentParser(description='Runs Protobuf to IFEX translator.')
    parser.add_argument('input', metavar='file.proto', type=str, help='path to input .proto file')

    try:
        args = parser.parse_args()
        proto_ast = protobuf_to_ifex.proto_ast_from_input(args.input)
        ifex_ast = protobuf_to_ifex.proto_to_ifex(proto_ast)
        print(protobuf_to_ifex.ifex_ast_as_yaml(ifex_ast))

    except Exception as e:
        print(f"ERROR: Conversion error resulting from {args.input}: {e}")
