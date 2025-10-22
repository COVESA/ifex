#!/usr/bin/python
# SPDX-FileCopyrightText: Copyright (c) 2023 Novaspring AB
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project

from collections import OrderedDict
import argparse
import sys
import yaml

# This file formats a YAML input in a fixed order ("sorted", basically).
# This facilitates reliable comparisons / diffing.

# The implementation is separated from diff/comparison-scripts to factor
# it out of that code. The first implementation is simple but it might be
# refined over time.


def ifex_stable_order(data):
    # To define a stable order we need two things.
    # 1. Use an OrderedDict instead of a normal dict
    # 2. Fill the dict by inputting the keys in the right order.
    if isinstance(data, dict):
        ordered_data = OrderedDict()
        # Insert the name first, but only if the node has a name.
        name = data.get("name")
        if name is not None:
            ordered_data["name"] = name

        # (Note: Make sure to use a loop instead of dict comprehension here
        # because dict comprehension supposedly does not guarantee key order?)
        for key in sorted(data.keys()):
            ordered_data[key] = ifex_stable_order(data[key])

        return ordered_data

    elif isinstance(data, list):
        return [ifex_stable_order(item) for item in data]

    else:
        return data


# If an ordered dict is printed as a normal dict we get a lot of unrelated
# metadata output.  Therefore, we need to specify how PyYAML shall represent an
# ordered dict: (PyYAML does not seemingly have OrderedDict support built in...?)
#
# Solution from:
# https://stackoverflow.com/questions/16782112/can-pyyaml-dump-dict-items-in-non-alphabetical-order
def represent_ordereddict(dumper, data):
    value = []

    for key, val in data.items():
        node_key = dumper.represent_data(key)
        node_val = dumper.represent_data(val)
        value.append((node_key, node_val))

    return yaml.nodes.MappingNode("tag:yaml.org,2002:map", value)


# ---------------------------------------------------------------------
# MAIN, used if this file is run standalone
# ---------------------------------------------------------------------
def usage():
    print(
        """
This script reorders IFEX (YAML) input into a stable ("sorted") order and prints the result back out.
The stable order is basically:
   0. Comments have no semantic meaning so they will be filtered out completely
   1. For dicts with key-value mappings, put the item 'name' first (if there is a key for 'name')
   2. Then, all other keys in alphabetical order
   3. Lists are not re-arranged (TODO: consider if lists should be sorted "by name" somehow?)
   4. Anything else remains in the input order.
"""
    )


def main():
    # Create the parser
    parser = argparse.ArgumentParser(
        description='Reorder IFEX (YAML) input ) input into a stable ("sorted") order and prints the result back out.'
    )
    # Add the arguments
    parser.add_argument("file1", help="Input file. (- to use STDIN)", nargs="?")

    # Parse the arguments
    args = parser.parse_args()

    if args.file1 is None:
        parser.print_help()
        usage()
        sys.exit(1)

    if args.file1 == "-":
        # Use STDIN if file is '-'
        data = yaml.safe_load(sys.stdin)
        out = ifex_stable_order(data)
    else:
        with open(args.file1, "r") as file:
            data = yaml.safe_load(file)
        out = ifex_stable_order(data)

    yaml.add_representer(OrderedDict, represent_ordereddict)
    print(yaml.dump(out, sort_keys=False))


if __name__ == "__main__":
    main()
