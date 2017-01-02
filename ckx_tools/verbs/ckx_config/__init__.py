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

from .cli import main
from .cli import prepare_arguments

# This describes this command to the loader
description = dict(
    verb='build',
    description="Builds a catkin workspace.",
    main=main,
    prepare_arguments=prepare_arguments,
    argument_preprocessor=argument_preprocessor,
)