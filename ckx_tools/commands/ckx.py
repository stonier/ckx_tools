#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/stonier/ckx_tools/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Commands verbs to be applied to the ckx entry point.
"""

##############################################################################
# Imports
##############################################################################

# import sys
import pkg_resources  # setuptools related helper that introspects the package

##############################################################################
# Methods
##############################################################################

CKX_COMMAND_VERB_GROUP = 'ckx_tools.commands.ckx.verbs'

def list_verbs():
    verbs = []
    for entry_point in pkg_resources.iter_entry_points(group=CKX_COMMAND_VERB_GROUP):
        verbs.append(entry_point.name)
    return verbs

def load_verb_description(verb_name):
    for entry_point in pkg_resources.iter_entry_points(group=CKX_COMMAND_VERB_GROUP):
        if entry_point.name == verb_name:
            return entry_point.load()

