#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/stonier/ckx_tools/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Implementation of the 'ckx build' verb.
"""

##############################################################################
# Imports
##############################################################################

import catkin_make.builder as builder  # extract_cmake_and_make_arguments, cmake_input_changed
import catkin_pkg.packages as catkin_packages
import ckx_tools.common as common
import ckx_tools.common as config_cache
import ckx_tools.console as console
import ckx_tools.terminal_color as terminal_color
import multiprocessing
import os
import re
import shutil
import subprocess
import sys

##############################################################################
# Methods
##############################################################################


def help_string():
    overview = 'Builds a catkin workspace.\n\n'
    instructions = "A typical workflow:\n \
 - 'ckx build --pre-clean : build and install the current workspace\n \
 - 'ckx build --install-rosdeps : install rosdeps\n \
 - 'ckx build' : build the current workspace\n \
 - 'ckx build --install : build and install the current workspace\n \
 - 'ckx build --tests/--run-tests : build and (optionally) run tests\n \
 "
    return overview + instructions


def prepare_arguments(parser):
    return parser


def main(args):
    return 0
