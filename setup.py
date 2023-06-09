#!/usr/bin/env python

from distutils import extension
import glob
from distutils.core import setup
from setuptools import find_packages

from ifex.templates import TemplatePath

def get_template_files():
      paths = []
      paths.extend(glob.glob(f"{TemplatePath}/*/*", recursive=False))   
                  
      print(f"{paths}")

      return paths


setup(name='ifex',
      version='0.1',
      description='Vehicle service catalog tools',
      author='',
      author_email='',
      url='https://github.com/covesa/ifex-tools',
      packages=find_packages(),
      package_data={
            'ifex': get_template_files()
      },
      entry_points='''
            [console_scripts]
            ifexgen=ifex.scripts.generator:ifex_generator_run
      '''
      )
