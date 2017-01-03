#!/usr/bin/env python

from setuptools import setup

# better to have this in the module somehow, but tricky
# to get that here *and* there and we don't exactly use
# the module version anywhere, so keep it simple...
# just here for now.
# import sys
# sys.path.insert(0, 'src')
__version__ = '0.1.1'

setup(name='ckx_tools',
      version=__version__,
      packages=['ckx_tools', 'catkin_make'],
      package_dir={'ckx_tools': 'ckx_tools', 'catkin_make': 'catkin_make'},
      scripts=[
          'scripts/ckx_make',
          'scripts/ckx_make_isolated',
      ],
      package_data={'ckx_tools': [
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
      author="Daniel Stonier",
      author_email="d.stonier@gmail.com",
      maintainer='Daniel Stonier',
      url="http://pypi.python.org/pypi/ckx_tools",
      download_url="https://github.com/stonier/ckx_tools.git",
      keywords=["Catkin", "ROS"],
      classifiers=[
          "Programming Language :: Python",
          "License :: OSI Approved :: BSD License"],
      description="Utilities for an extreme catkin development environment",
      long_description="Refer to the documentation at https://github.com/stonier/ckx_tools.",
      license="BSD",
      entry_points={
          'console_scripts': [
              'ckx = ckx_tools.__main__:main',
          ],
          'ckx_tools.commands.ckx.verbs': [
              'ws = ckx_tools.verbs.ckx_ws:description',
              'config = ckx_tools.verbs.ckx_config:description',
              'build = ckx_tools.verbs.ckx_build:description',
              'settings = ckx_tools.verbs.ckx_settings:description',
          ],
      }
      # not picked up by distutils, need to install setuptools above
      # but even then I'm not getting much happening
      # install_requires = [
      #     'pyyaml',
      #     'python-catkin-pkg',
      # ],
      )

# This no longer works...it has to be a special parsable syntax of pypi's.
#      long_description = open('README.md').read(),
