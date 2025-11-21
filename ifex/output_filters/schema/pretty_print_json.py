# SPDX-License-Identifier: MPL-2.0

# =======================================================================
# (C) 2023 MBition GmbH
# Author: Gunnar Andersson
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# =======================================================================


"""
Read JSON, dump it out in pretty/indented format
"""

# Generally I prefer the 'jq' tool for this but it seems more consistent
# to use a python solution even if it means adding json package as a new
# dependency.

import json
import sys

# Not much error-checking here. Just use it correctly.
input_file = sys.argv[1]
with open(input_file, 'r') as file:
    print(json.dumps(json.load(file), indent=2))
