#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/stonier/ckx_tools/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
The primary entry point to the ckx scripts.
"""

##############################################################################
# Imports
##############################################################################

import sys

##############################################################################
# Methods
##############################################################################

def main(args=None):
    """
    Primary entry point for the ckx scripts.
    """
    if args is None:
        args = sys.argv[1:]

    print("CKX entry point")