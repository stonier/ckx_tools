#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/stonier/ckx_tools/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Module implementing the 'ckx build' verb.
"""

##############################################################################
# Imports
##############################################################################

from ckx_tools.argument_parsing import argument_preprocessor

from . import main

##############################################################################
# Plugin Description
##############################################################################

description = dict(
    verb='make',
    description="builds a catkin workspace (yujin legacy style)",
    main=main.main,
    prepare_arguments=main.prepare_arguments,
    argument_preprocessor=argument_preprocessor,
)
