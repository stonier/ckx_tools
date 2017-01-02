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

def prepare_arguments(parser):
    parser.description = """\
Build one or more packages in a catkin workspace.
This invokes `CMake`, `make`, and optionally `make install` for either all
or the specified packages in a catkin workspace.\
"""

def main(opts):
    pass