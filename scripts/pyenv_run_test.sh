#!/bin/sh -xe

# SPDX-FileCopyrightText: Copyright (c) 2023 Novaspring AB
# SPDX-License-Identifier: MPL-2.0
#
# This file is part of IFEX project
# ---------------------------------------------------------------------------

# Normalize directory location
cd "$(dirname "$0")"  # (the directory this script is in)
cd ..

PYTHON_VERSION=$(cat .python-version)

# This is a simple script that will set up a virtual python environment and run
# the test suite in one operation.

# Set up python environment install prerequisites and the IFEX module itself
python -m venv venv
set +x 
source venv/bin/activate
set -x
pyenv install --skip-existing $PYTHON_VERSION
pyenv local $PYTHON_VERSION
python -m pip install -r requirements.txt
python -m pip install pyyaml jinja2 pytest anytree

# Run setup.py but via pip, to install IFEX module in develop mode
pip install --editable .  # (a.k.a. setup.py develop mode)

# Let's check
python --version

# Run specifically only our own tests.  (Sometimes other modules with tests are in the working directory)
pytest tests/

