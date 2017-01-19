#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/stonier/ckx_tools/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Module implementing the 'ckx rosdoc' verb.
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
    verb='rosdoc',
    description="Documents catkin packages for a specified workspace profile.",
    main=cli.main,
    prepare_arguments=cli.prepare_arguments,
)
