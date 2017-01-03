#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/stonier/ckx_tools/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Module implementing argument parsing for the entire suite.
"""

##############################################################################
# Imports
##############################################################################


def argument_preprocessor(args):
    """Perform processing of argument patterns which are not captured by
    argparse, before being passed to argparse
    :param args: system arguments from which special arguments need to be extracted
    :type args: list
    :returns: a tuple contianing a list of the arguments which can be handled
    by argparse and a dict of the extra arguments which this function has
    extracted
    :rtype: tuple
    """
    return args
