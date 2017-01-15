#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/stonier/ckx_tools/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Module implementing the 'ckx ws' verb.
"""

##############################################################################
# Imports
##############################################################################

from . import cli

##############################################################################
# Plugin Description
##############################################################################

# This describes this command to the loader
description = dict(
    verb='ws',
    description="Creates and populates a catkin tools workspace",
    main=cli.main,
    prepare_arguments=cli.prepare_arguments,
)
