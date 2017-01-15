#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/stonier/ckx_tools/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Implementation of the 'ckx ws' verb.
"""

##############################################################################
# Imports
##############################################################################

import catkin_tools.argument_parsing as argument_parsing

from catkin_tools.terminal_color import ColorMapper
color_mapper = ColorMapper()
clr = color_mapper.clr

##############################################################################
# Entry Point API
##############################################################################

def help_string():
    overview = clr('@{gf}Handles rosdeps for a specified workspace profile.@|\n\n')
    instructions = clr("  \
@!Minimal Examples@|\n\n  \
  @{cf}ckx rosdep --install@| : @{yf}install rosdeps for the active profile in the enclosing workspace@|\n  \
  @{cf}ckx rosdep --list@|    : @{yf}list all rosdep keys for the active profile in the enclosing workspace@|\n\n  \
@!Target Profile/Workspace Examples@|\n\n  \
  @{cf}ckx rosdep --workspace ~/foo_ws --install@| : @{yf}for the active profile in the specified workspace@|\n  \
  @{cf}ckx rosdep --profile native --install@| : @{yf}for the specified profile in the enclosing workspace@|\n  \
 ")
    return overview + instructions

def prepare_arguments(parser):
    parser.description = help_string()
    # Workspace / profile args
    argument_parsing.add_context_args(parser)
    add = parser.add_argument
    add('--install', '-i', action='store_true', default=False,
        help='Install all rosdeps for this build profile (including underlays)')
    add('--list', '-l', action='store_true', default=False,
        help='List all rosdep keys required by this build profile (including underlays)')
    return parser


def main(opts):
    if opts.install:
        print("Installing rosdeps")
        return 0
    if opts.list:
        print("Listing rosdep keys")
        return 0
    return 0
