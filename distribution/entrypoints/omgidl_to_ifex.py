# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# User-invocation script for OMG IDL to IFEX conversion

from ifex.models.omgidl.omgidl_lark import get_ast_from_idl_file
from ifex.input_filters.omgidl.omgidl_to_ifex import omgidl_to_ifex
from ifex.models.common.ast_utils import ast_as_yaml
import argparse


def omgidl_to_ifex_run():

    parser = argparse.ArgumentParser(description='Runs OMG IDL to IFEX translator.')
    parser.add_argument('input', metavar='file.idl', type=str, help='path to input .idl file')

    try:
        args = parser.parse_args()
        idl_ast = get_ast_from_idl_file(args.input)
        ifex_ast = omgidl_to_ifex(idl_ast)
        print(ast_as_yaml(ifex_ast))

    except FileNotFoundError:
        print(f"ERROR: File not found: {args.input}")
    except Exception as e:
        print(f"ERROR: Conversion error for {args.input}: {e}")
        raise


if __name__ == "__main__":
    omgidl_to_ifex_run()
