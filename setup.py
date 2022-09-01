#!/usr/bin/env python

from distutils.core import setup
from importlib.metadata import entry_points

setup(name='vsc',
      version='0.1',
      description='Vehicle service catalog tools',
      author='',
      author_email='',
      url='https://github.com/covesa/vsc-tools',
      packages=['vsc','tests'],
      entry_points='''
            [console_scripts]
            vscgen=vsc.scripts.generator:vsc_generator_run
      '''
      )
