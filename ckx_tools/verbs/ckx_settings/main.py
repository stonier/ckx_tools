#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/stonier/ckx_tools/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Implementation of the 'ckx settings' verb.
"""

##############################################################################
# Imports
##############################################################################

import ckx_tools.common as common
import ckx_tools.console as console
import sys

##############################################################################
# Methods
##############################################################################


def help_string():
    overview = '\nThis is a convenience script for configuring ckx tools settings.\n\n'
    instructions = " \
 - 'ckx settings --get-default-track' : return the currently configured default track.\n \
 - 'ckx settings --set-default-track hydro' : save this track as the default track in ckx_tools_home.\n \
 - 'ckx settings --get-rosinstall-database-uri' : return the currently configured rosinstall database uri.\n \
 - 'ckx settings --set-rosinstall-database-uri' : save this url as the default rosinstall database uri.\n \
 "
    return overview + instructions


def prepare_arguments(parser):
    parser.add_argument('--get-default-track', action='store_true', help='print the default track that is being followed to screen')
    parser.add_argument('--set-default-track', action='store', default=None, help='set a new default track to work from %s' % common.VALID_TRACKS)
    parser.add_argument('--get-rosinstall-database-uri', action='store_true', help='print the default rosinstall database uri')
    parser.add_argument('--set-rosinstall-database-uri', action='store', default=None, help='set a new default  rosinstall database uri')
    return parser


def main(args):
    '''
      Process the workspace command and return success or failure to the calling script.
    '''
    if args.get_default_track:
        # console.pretty_print("\nDefault Track: ", console.cyan)
        # console.pretty_println("%s\n" % get_default_track(), console.yellow)
        print common.get_default_track()
        sys.exit(0)
    if args.set_default_track:
        console.pretty_print("\nNew Default Track: ", console.cyan)
        console.pretty_println("%s\n" % common.set_default_track(args.set_default_track), console.yellow)
        sys.exit(0)
    if args.get_rosinstall_database_uri:
        print common.get_rosinstall_database_uri()
        sys.exit(0)
    if args.set_rosinstall_database_uri:
        console.pretty_print("\nNew Rosisntall Database Uri: ", console.cyan)
        console.pretty_println("%s\n" % common.set_rosinstall_database_uri(args.set_rosinstall_database_uri), console.yellow)
        sys.exit(0)
    print("%s" % help_string())
    return 0
