# SPDX-FileCopyrightText: Copyright (c) 2022 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

from vsc.model.vsc_generator import gen
from vsc.model.vsc_parser import get_ast_from_file
import argparse, dacite

def vsc_generator_run():
    parser = argparse.ArgumentParser(description='Runs vehicle service catalog code generator.')
    parser.add_argument('input', metavar='input', type=str,
                        help='input.yaml-file (path)')
    parser.add_argument('template', metavar='template', type=str, nargs='?',
                        help='output-template-file (name only, not path)')
    try:
        args = parser.parse_args()
    except dacite.UnexpectedDataError as e:
        print(f"ERROR: Read error resulting from {filename}: {e}")

    ast = get_ast_from_file(args.input)

    templatename = args.template

    print(gen(ast, templatename))


if __name__ == "__main__":
    vsc_generator_run()