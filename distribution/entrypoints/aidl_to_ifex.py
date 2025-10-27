# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# User-invocation script for Android IDL (AIDL) to IFEX conversion

from ifex.models.aidl.aidl_lark import get_ast_from_aidl_file
from ifex.input_filters.aidl.aidl_to_ifex import aidl_to_ifex
from ifex.models.common.ast_utils import ast_as_yaml
import argparse


def aidl_to_ifex_run():

    parser = argparse.ArgumentParser(description='Runs Android IDL (AIDL) to IFEX translator.')
    parser.add_argument('input', metavar='file.aidl', type=str, help='path to input .aidl file')

    try:
        args = parser.parse_args()
        aidl_ast = get_ast_from_aidl_file(args.input)
        ifex_ast = aidl_to_ifex(aidl_ast)
        print(ast_as_yaml(ifex_ast))

    except FileNotFoundError:
        print(f"ERROR: File not found: {args.input}")
    except Exception as e:
        print(f"ERROR: Conversion error for {args.input}: {e}")
        raise


if __name__ == "__main__":
    aidl_to_ifex_run()
