#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/stonier/ckx_tools/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Module implementing global settings for the 'ckx' tool.
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
    verb='settings',
    description="set and get global settings for the 'ckx' ",
    main=cli.main,
    prepare_arguments=cli.prepare_arguments,
    argument_preprocessor=argument_preprocessor,
)
