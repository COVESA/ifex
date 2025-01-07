# SPDX-FileCopyrightText: Copyright (c) 2023 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# User-invocation script for D-Bus generation
# (small wrapper around the main implementation)

from models.ifex.ifex_parser import get_ast_from_yaml_file
from output_filters.DBus import dbus_generator
import argparse, dacite

def ifex_dbus_generator_run():
    parser = argparse.ArgumentParser(description='Runs IFEX to D-Bus XML translator.')
    parser.add_argument('input', metavar='ifex-input-file', type=str, help='path to input IFEX (YAML) file')

    try:
        args = parser.parse_args()
        dbus_generator.main_generate(args.input)

    except dacite.UnexpectedDataError as e:
        print(f"ERROR: Read error resulting from {filename}: {e}")

if __name__ == "__main__":
    ifex_dbus_generator_run()
