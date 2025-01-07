# SPDX-FileCopyrightText: Copyright (c) 2022 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

from models.ifex.ifex_generator import jinja_env
from models.ifex.ifex_generator import gen
from models.ifex.ifex_parser import get_ast_from_yaml_file
import argparse, dacite

def ifex_generator_run():
    parser = argparse.ArgumentParser(description='Runs generic IFEX code generator with given template(s).')
    parser.add_argument('input', metavar='ifex-input-file', type=str, help='path to input IFEX (YAML) file')
    parser.add_argument('-d','--template-directory', dest='templatedir', metavar='templates-dir-name', type=str, required=True,
                        help='choose output type by stating the template directory, as an absolute path or a sub-directory of templates/')
    parser.add_argument('template', metavar='root-template', type=str, nargs='?',
                        help='Top-level template file name (default : first file starting with AST_....)')

    try:
        args = parser.parse_args()
    except dacite.UnexpectedDataError as e:
        print(f"ERROR: Read error resulting from {filename}: {e}")

    ast = get_ast_from_yaml_file(args.input)

    jinja_env.__init__(args.templatedir)
    jinja_env.set_template_env( gen=gen )
    print(gen(ast))


if __name__ == "__main__":
    ifex_generator_run()
