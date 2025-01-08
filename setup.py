#!/usr/bin/env python

import glob
from setuptools import setup
from setuptools import find_packages

from output_filters.templates import TemplateDir

def get_template_files():
      paths = []
      paths.extend(glob.glob(f"{TemplateDir.TemplatePath}/*/*", recursive=False))   
      return paths

setup(name='ifex',
      version='1.4',
      description='Interface Exchange Framework (IFEX) tools',
      author='',
      author_email='',
      url='https://github.com/COVESA/ifex',
      packages=find_packages(),
      package_data={
            'ifex': get_template_files()
      },
      entry_points='''
            [console_scripts]
            ifexgen=packaging.entrypoints.generator:ifex_generator_run
            ifexgen_dbus=packaging.entrypoints.generator_dbus:ifex_dbus_generator_run
            ifexconv_protobuf=packaging.entrypoints.protobuf_ifex:protobuf_to_ifex_run
      '''
      )
