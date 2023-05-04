# SPDX-FileCopyrightText: Copyright (c) 2022 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

from ifex.model.ifex_generator import gen
from ifex.model.ifex_parser import get_ast_from_yaml_file
import argparse, dacite

def ifex_generator_run():
    parser = argparse.ArgumentParser(description='Runs IFEX code generator.')
    parser.add_argument('input', metavar='input', type=str,
                        help='input.yaml-file (path)')
    parser.add_argument('template', metavar='template', type=str, nargs='?',
                        help='output-template-file (name only, not path)')
    try:
        args = parser.parse_args()
    except dacite.UnexpectedDataError as e:
        print(f"ERROR: Read error resulting from {filename}: {e}")

    ast = get_ast_from_yaml_file(args.input)

    templatename = args.template

    print(gen(ast, templatename))


if __name__ == "__main__":
    ifex_generator_run()
