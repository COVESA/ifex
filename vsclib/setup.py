#!/usr/bin/env python3
#
# (C) 2022 MBition GmbH
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


import setuptools

long_description="""Library to create, validate, and genreate VSC files
This library can be used by translators parsing other IDL files (FrancaIDL, etc)
to build up an equivalent VSC structure, make sure that all datatype can
resolve, and generate a python dictionary that can be written out as
as VSC YAM file."""

setuptools.setup(
    name="vsclib",
    version="0.0.1",
    author="Magnus Feuer",
    author_email="magnus.feuer@mercedes-benz.com",
    description="VSC Generator Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/COVESA/vsclib",
    packages=setuptools.find_packages(),
    scripts=["vsc_test.py" ],
    data_files=[],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
