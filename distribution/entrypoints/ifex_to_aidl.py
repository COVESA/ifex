# SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# User-invocation script for IFEX to Android IDL (AIDL) generation

from ifex.models.ifex.ifex_parser import get_ast_from_yaml_file
from ifex.output_filters.aidl.ifex_to_aidl import ifex_to_aidl
from ifex.output_filters.aidl.aidl_generator import aidl_to_text
import argparse

def ifex_to_aidl_run():

    parser = argparse.ArgumentParser(description='Runs IFEX to Android IDL (AIDL) translator.')
    parser.add_argument('input', metavar='ifex-input-file', type=str, help='path to input IFEX (YAML) file')

    try:
        args = parser.parse_args()
        ifex_ast = get_ast_from_yaml_file(args.input)
        aidl_files = ifex_to_aidl(ifex_ast)
        print(aidl_to_text(aidl_files))

    except FileNotFoundError:
        print(f"ERROR: File not found: {args.input}")
    except Exception as e:
        print(f"ERROR: Conversion error for {args.input}: {e}")
        raise

if __name__ == "__main__":
    ifex_to_aidl_run()
