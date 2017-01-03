#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/stonier/ckx_tools/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Module implementing the 'ckx config' verb.
"""

##############################################################################
# Imports
##############################################################################

from ckx_tools.argument_parsing import argument_preprocessor

from . import cli

##############################################################################
# Plugin Description
##############################################################################

description = dict(
    verb='config',
    description="configures a catkin workspace",
    main=cli.main,
    prepare_arguments=cli.prepare_arguments,
    argument_preprocessor=argument_preprocessor,
)
