#!/usr/bin/env python

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="ifex",
    version="1.5",
    description="Interface Exchange Framework (IFEX) tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="COVESA",
    author_email="",
    url="https://github.com/COVESA/ifex",
    project_urls={
        "Bug Tracker": "https://github.com/COVESA/ifex/issues",
        "Documentation": "https://covesa.github.io/ifex",
        "Source Code": "https://github.com/COVESA/ifex",
    },
    packages=find_packages(),
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license="MPL-2.0",
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ifexgen=distribution.entrypoints.generator:ifex_generator_run",
            "ifexgen_dbus=distribution.entrypoints.generator_dbus:ifex_dbus_generator_run",
            "ifexconv_protobuf=distribution.entrypoints.protobuf_ifex:protobuf_to_ifex_run",
            "aidl_to_ifex=distribution.entrypoints.aidl_to_ifex:aidl_to_ifex_run",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
