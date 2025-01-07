#!/usr/bin/python

# SPDX-FileCopyrightText: Copyright (c) 2023 Novaspring AB
# SPDX-License-Identifier: MPL-2.0

# This file is part of the IFEX project

import argparse
import subprocess
import tempfile
import yaml
from collections import OrderedDict
from models.ifex.stable_sort_ifex import ifex_stable_order, represent_ordereddict

# The program compares two IFEX (YAML) files after normalizing ("sorting",
# basically) the order of elements so that the comparison becomes more relevant.

# The normal unix diff command seems to give the most useful output:
def diff_files_with_external_program(path1, path2):
    """Run standard unix diff program on the given paths"""
    # diff returns an error code if there is a difference => use run with check
    # False to ignore the error, (instead of check_output())
    return subprocess.run(
        ["diff", path1, path2], text=True, check=False, stdout=subprocess.PIPE
    ).stdout


# Alternative, using difflib
def diff_files(path1, path2):
    import difflib

    """Use difflib to print the difference between the given files"""
    with open(path1, "r") as f1:
        l1 = f1.readlines()
    with open(path2, "r") as f2:
        l2 = f2.readlines()

    for line in difflib.context_diff(l1, l2):
        print(line, end="")


def stable_order_file(file1):
    """Writes a new file containing the YAML content with keys in order, and
    returns the file name"""
    with open(file1, "r") as f1:
        with tempfile.NamedTemporaryFile("w", delete=False) as f2:
            yaml.add_representer(OrderedDict, represent_ordereddict)
            f2.write(yaml.dump(ifex_stable_order(yaml.safe_load(f1)), sort_keys=False))
            return f2.name

    return None  # Will fail on exception before this


def compare_yaml_files(file1, file2):
    """Order the keys of the given file names, write them to new temporary
    files, then diff the results"""
    f1 = stable_order_file(file1)
    f2 = stable_order_file(file2)

    print("Stable sorting...")
    print(f"temporary files are {file1} -> {f1}, {file2} -> {f2}")
    print("Comparing files:")
    return diff_files_with_external_program(f1, f2)


# ---------------------------------------------------------------------
# MAIN, used if this file is run standalone
# ---------------------------------------------------------------------


def main():
    # Create the parser
    parser = argparse.ArgumentParser(
        description="Compare IFEX (YAML) file contents, after normalizing order of elements."
    )

    # Add the arguments
    parser.add_argument("file1", help="First, original file")
    parser.add_argument("file2", help="Second, possibly changed file")
    parser.add_argument(
        "-p",
        action="store_true",
        default=False,
        help="Only print the created temporary file paths, for use with an external diff program",
    )

    # Parse the arguments
    args = parser.parse_args()

    # If print filenames only
    if args.p:
        print(stable_order_file(args.file1))
        print(stable_order_file(args.file2))
        return

    # Otherwise, output diff as well
    print(compare_yaml_files(args.file1, args.file2))


if __name__ == "__main__":
    main()
