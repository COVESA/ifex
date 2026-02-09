#!/bin/sh -xe

# SPDX-FileCopyrightText: Copyright (c) 2023 Novaspring AB
# SPDX-License-Identifier: MPL-2.0
#
# This file is part of IFEX project
# ---------------------------------------------------------------------------

# Normalize directory location
cd "$(dirname "$0")" # (the directory this script is in)
cd ..

# This is a simple script that will set up a virtual python environment and run
# the test suite in one operation.

# Set up python environment install prerequisites and the IFEX module itself
set -x
uv python install
uv sync --group=dev

# Let's check
uv run python --version

# Run specifically only our own tests.  (Sometimes other modules with tests are in the working directory)

uv run pytest tests/
