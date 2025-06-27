# SPDX-FileCopyrightText: Copyright (c) 2025 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

"""Determine the type of an input file by validating it with multiple schemas."""

from output_filters.schema.validate import schema_check
import sys

def get_matching_schemas(input_file : str, schemas : list):
    checkit = lambda f : schema_check(input_file, f, quiet=True)
    return list(filter(checkit, schemas))

# Some other possibly useful entry points for usage from other modules:
def is_single_match(input_file : str, schemas : list):
    return len(get_matching_schemas(input_file, schemas)) == 1

# Note - this one intended to be called _only if_ is_single_match is True
def identify_file(input_file : str, schemas : list):
    matching = get_matching_schemas(input_file, schemas)
    if len(matching) == 1:
        return matching[0]
    else:
        return None

# Can also be used as an executable script directly:
if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print("Usage: identify_layer.py file.ifex schema.json [schema2.json, schema3... etc]")
        sys.exit(1)

    input_file = sys.argv[1]
    schemas = list(set(sys.argv[2:]))  # (remove any duplicates)
    matching = get_matching_schemas(input_file, schemas)
    num_match = len(matching)
    if num_match == 0:
        print("No match.")
        sys.exit(1)
    elif num_match > 1:
        print("Could not identify file because more than one given schema seems to be matching!")
        for m in matching:
            print("  - " + m)
        sys.exit(num_match)
    else:
        print(f"The input file is of type: {matching[0]}")
        sys.exit(0)
