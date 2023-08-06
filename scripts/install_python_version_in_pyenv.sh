#!/bin/sh -x

# SPDX-FileCopyrightText: Copyright (c) 2023 Novaspring AB
# SPDX-License-Identifier: MPL-2.0
#
# This file is part of IFEX project
# ---------------------------------------------------------------------------

# Go to project directory
cd "$(dirname "$0")"
cd ..

if [ -z "$1" ] ; then
   echo "usage: $0 <python-version-to-install>"
   exit 1
fi

# Fallback version is local to this file, and basically the setup is buggy if it needs to be used.
FALLBACK_VERSION=3.10.10
VERSION=${1:-$FALLBACK_VERSION}

# initialize standard pyenv environment
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

# Install the required version using pyenv.
pyenv install --skip-existing $VERSION
