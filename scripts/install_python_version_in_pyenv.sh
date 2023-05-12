#!/bin/sh -x

# SPDX-FileCopyrightText: Copyright (c) 2023 Novaspring AB
# SPDX-License-Identifier: MPL-2.0
#
# This file is part of IFEX project
# ---------------------------------------------------------------------------

# This is local to this file, and basically the setup is buggy if this needs to be used.
FALLBACK_VERSION=3.10.10

cd "$(dirname "$0")"
cd ..

# pyenv writes a local .python-version file to remember which is the currently
# enabled version in the environment. We store .default-python-version in the
# repository to define the default version used for testing.

# Get python version from stored .python-version file
# In case the file does not exist, assign a default version
DEFAULT_PYTHON_VERSION=$(cat .default-python-version)
VERSION=${DEFAULT_PYTHON_VERSION:-$FALLBACK_VERSION}

# Install the required version using pyenv.
pyenv install --skip-existing $VERSION
