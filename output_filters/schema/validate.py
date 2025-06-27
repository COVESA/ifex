# SPDX-License-Identifier: MPL-2.0

# =======================================================================
# (C) 2023 MBition GmbH
# Author: Gunnar Andersson
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# =======================================================================

"""Validate a JSON or YAML file, against a JSON schema"""

from pathlib import Path
import json
import jsonschema
import sys
import yaml


def schema_check(input_file, schema_file, quiet = True):

    if quiet:
        _print = lambda *args, **kwargs : None
    else:
        _print = print

    suffix = Path(input_file).suffix

    # This is a special case to handle also JSON inputs, even if YAML is preferred in most cases
    if suffix == '.json':
       _print("Loading input as JSON")
       load_function=json.load
    # .yaml or .ifex is preferred, but we assume YAML also if unknown:
    else:
       _print("Loading input as YAML")
       load_function=yaml.safe_load

    # Load input data from file
    with open(input_file, 'r') as file:
        input_data = load_function(file)

    # Load JSON-schema from file
    with open(schema_file, 'r') as file:
        schema_data = json.load(file)

    # Validate data against JSON-schema
    try:
        jsonschema.validate(input_data, schema_data)
        _print(f"{input_file} is valid according to the schema.")
        return True
    except jsonschema.exceptions.ValidationError as e:
        _print(f"\n{input_file} violates the schema.")
        if len(e.path) == 0:
            _print("The error appears to be at the top-level of the file")
        else:
            _print("The path leading up to the error is:\n")
            while len(e.path) > 0:
                node=e.path.popleft()
                if type(node) is int:
                    # Change indexing from zero-based to one-based and report the item number
                    _print(f'[item #{int(node)+1}]->', end="")
                else:
                    _print(f'{node}->')
        _print(f"ERROR: {e.message}")
        _print("\n(Numbers indicate the item number in a list of items.)")
        return False

if __name__ == '__main__':

    input_file = sys.argv[1]
    schema_file = sys.argv[2]

    if len(sys.argv) > 3 and sys.argv[3] == '--quiet':
        ok = schema_check(input_file, schema_file, quiet=True)
    else:
        ok = schema_check(input_file, schema_file, quiet=False)

    if ok:
        sys.exit(0)
    else:
        sys.exit(1)
