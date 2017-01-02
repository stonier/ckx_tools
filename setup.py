#!/usr/bin/env python
#from distutils.core import setup
#import sys

# Setuptools' sdist does not respect package_data
# from setuptools import setup, find_packages
# Distutils however, does not respect install_requires
# Distutils is in python, setuptools is outside
# Setuptools is now the defacto default though
#try:
#    from setuptools import setup
#except ImportError:
#    from distutils.core import setup
from distutils.core import setup

import sys
sys.path.insert(0, 'src')

# better to have this in the module somehow, but tricky
# to get that here *and* there and we don't exactly use
# the module version anywhere, so keep it simple...
# just here for now.
__version__ = '0.1.1'

setup(name='ckx_tools',
      version= __version__,
      packages=['ckx_tools', 'catkin_make'],
      package_dir = {'ckx_tools':'src/ckx_tools', 'catkin_make':'src/catkin_make'},
      scripts = [
           'scripts/ckx_init_workspace',
           'scripts/ckx_init_build',
           'scripts/ckx_make',
           'scripts/ckx_make_isolated',
           'scripts/ckx_tools_settings',
      ],
      package_data = {'ckx_tools': [
           'cmake/*',
           'templates/init_build/.bashrc',
           'templates/init_build/konsole',
           'templates/init_build/gnome-terminal',
           'templates/init_build/eclipse',
           'templates/init_build/android-studio',
           'toolchains/buildroot/*',
           'toolchains/ubuntu/*',
           'toolchains/code_sourcery/*',
	   'toolchains/nexell/*',
           'platforms/default.cmake',
           'platforms/generic/*',
           'platforms/arm/*',
           'platforms/intel/*',
           'data/*'
           ]},
      author = "Daniel Stonier",
      author_email = "d.stonier@gmail.com",
      maintainer='Daniel Stonier',
      url = "http://pypi.python.org/pypi/ckx_tools",
      download_url = "https://github.com/stonier/ckx_tools.git",
      keywords = ["Catkin", "ROS"],
      classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License" ],
      description = "Utilities for an extreme catkin development environment",
      long_description = "Refer to the documentation at https://github.com/stonier/ckx_tools.",
      license = "BSD",
      # not picked up by distutils, need to install setuptools above
      # but even then I'm not getting much happening
      # install_requires = [
      #     'pyyaml',
      #     'python-catkin-pkg',
      # ],
      )

# This no longer works...it has to be a special parsable syntax of pypi's.
#      long_description = open('README.md').read(),

