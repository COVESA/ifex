#!/bin/sh -x

# SPDX-FileCopyrightText: Copyright (c) 2023 Novaspring AB
# SPDX-License-Identifier: MPL-2.0
#
# This file is part of IFEX project
# ---------------------------------------------------------------------------

cd "$(dirname "$0")"

# Get python version from stored .python-version file
# In case the file does not exist, assign a default version
REQUESTED=$(cat .python-version)
VERSION=${REQUESTED:-3.10.10}

# Install the required version using pyenv.
pyenv install --skip-existing $VERSION
