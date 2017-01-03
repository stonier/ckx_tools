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

from ckx_tools.verbs.ckx_settings import main

##############################################################################
# Plugin Description
##############################################################################

description = dict(
    verb='settings',
    description="set and get global settings for the 'ckx' ",
    main=main.main,
    prepare_arguments=main.prepare_arguments,
    argument_preprocessor=argument_preprocessor,
)
