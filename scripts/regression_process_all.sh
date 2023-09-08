#!/bin/sh -x
# SPDX-FileCopyrightText: Copyright (c) 2023 MBition GmbH.
# SPDX-License-Identifier: MPL-2.0

# This file is part of IFEX project

# Script to be used as argument to regression_test.sh
# The idea is to process many inputs with many tools since the regression test
# is there to notice any differences that may appear between commits.

# Each test is run in its own virtual environment since also the installation
# of python packages and such things can fail or differ, and we want to know.

rm -rf venv
python -m venv venv
. venv/bin/activate
python setup.py develop
pip install -r requirements.txt

git clone https://github.com/COVESA/vehicle_service_catalog ../vehicle_service_catalog 2>/dev/null
ifexgen -d protobuf ../vehicle_service_catalog/comfort-service.yml
ifexgen -d simple ../vehicle_service_catalog/comfort-service.yml
ifexgen -d dtdl ../vehicle_service_catalog/comfort-service.yml
ifexgen -d sds-bamm ../vehicle_service_catalog/comfort-service.yml
ifexgen_dbus ../vehicle_service_catalog/comfort-service.yml
