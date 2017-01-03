#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/stonier/ckx_tools/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Module implementing the 'ckx isolated' verb.
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
    verb='isolated',
    description="builds packages in a catkin workspace in isolation",
    main=main.main,
    prepare_arguments=main.prepare_arguments,
    argument_preprocessor=argument_preprocessor,
)
