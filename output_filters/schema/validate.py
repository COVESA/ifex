# SPDX-License-Identifier: MPL-2.0

# =======================================================================
# (C) 2023 MBition GmbH
# Author: Gunnar Andersson
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# =======================================================================

import sys
import yaml
import json
import jsonschema
from pathlib import Path

input_file = sys.argv[1]
schema_file = sys.argv[2]

suffix = Path(input_file).suffix

# This is a special case to handle also JSON inputs, even if YAML is preferred in most cases
if suffix == '.json':
   print("Loading input as JSON")
   load_function=json.load
# .yaml or .ifex is preferred, but we assume YAML also if unknown:
else:
   print("Loading input as YAML")
   load_function=yaml.safe_load

# Load input data from file
with open(input_file, 'r') as file:
    input_data = load_function(file)

# Load JSON-schema from file
with open(schema_file, 'r') as file:
    schema_data = json.load(file)

# Validate YAML data against JSON-schema
try:
    jsonschema.validate(input_data, schema_data)
    print(f"{input_file} is valid according to the schema.")
except jsonschema.exceptions.ValidationError as e:
    print(f"\n{input_file} violates the schema.")
    if len(e.path) == 0:
        print("The error appears to be at the top-level of the file")
    else:
        print("The path leading up to the error is:\n")
        while len(e.path) > 0:
            node=e.path.popleft()
            if type(node) is int:
                # Change indexing from zero-based to one-based and report the item number
                print(f'[item #{int(node)+1}]->', end="")
            else:
                print(f'{node}->')
    print(f"ERROR: {e.message}")
    print("\n(Numbers indicate the item number in a list of items.)")
