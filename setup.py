#!/usr/bin/env python

import glob
from setuptools import setup
from setuptools import find_packages

setup(name='ifex',
      version='1.5',
      description='Interface Exchange Framework (IFEX) tools',
      author='',
      author_email='',
      url='https://github.com/COVESA/ifex',
      packages=find_packages(),
      entry_points='''
            [console_scripts]
            ifexgen=packaging.entrypoints.generator:ifex_generator_run
            ifexgen_dbus=packaging.entrypoints.generator_dbus:ifex_dbus_generator_run
            ifexconv_protobuf=packaging.entrypoints.protobuf_ifex:protobuf_to_ifex_run
      '''
      )
