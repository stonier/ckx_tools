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

import argparse
import sys
import pkg_resources  # setuptools related helper that introspects the package

from . import common
from . import terminal_color

from .terminal_color import fmt

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


def default_argument_preprocessor(args):
    extras = {}
    return args, extras


def create_subparsers(parser, verbs):
    verbs = sorted(verbs)
    verb_array_str = '[' + ' | '.join(verbs) + ']'
    verb_list_str = 'Call `ckx VERB -h` for help on each verb listed below:\n'
    for verb in verbs:
        desc = load_verb_description(verb)
        verb_list_str += '\n  %s\t%s' % (desc['verb'], desc['description'])

    subparsers = parser.add_subparsers(
        title='ckx command',
        metavar=verb_array_str,
        description=verb_list_str,
        dest='verb'
    )

    argument_preprocessors = {}

    for verb in verbs:
        desc = load_verb_description(verb)
        cmd_parser = subparsers.add_parser(desc['verb'], description=desc['description'], formatter_class=argparse.RawDescriptionHelpFormatter)
        cmd_parser = desc['prepare_arguments'](cmd_parser)
        cmd_parser.set_defaults(main=desc['main'])
        if 'argument_preprocessor' in desc:
            argument_preprocessors[verb] = desc['argument_preprocessor']
        else:
            argument_preprocessors[verb] = default_argument_preprocessor

    return argument_preprocessors


def ckx_main(sysargs):
    try:
        common.initialise_ckx_tools_home()
    except RuntimeError as e:
        sys.exit("Failed to initialise the settings dir [{0}][{1}]".format(common.ckx_tools_home(), str(e)))

    # the top parser dog
    parser = argparse.ArgumentParser(
        description="catkin 'x' command interface",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--test-colors',
        action='store_true',
        default=False,
        help="prints a color test pattern to the screen and then quits, all other arguments are ignored"
    )
    parser.add_argument('--version', action='store_true', default=False, help="Prints the ckx_tools version.")
    color_control_group = parser.add_mutually_exclusive_group()
    color_control_group.add_argument(
        '--force-color',
        action='store_true',
        default=False,
        help='forces catkin to output in color, even when the terminal does not appear to support it.'
    )
    color_control_group.add_argument(
        '--no-color',
        action='store_true',
        default=False,
        help='forces catkin to not use color in the output, regardless of the detect terminal type.'
    )

    ####################
    # Verb Handling
    ####################
    verbs = list_verbs()
    # Create the subparsers for each verb and collect the argument preprocessors
    argument_preprocessors = create_subparsers(parser, verbs)

    args = parser.parse_args(sysargs)
#     # Help out by collecting unknown args in the unknown_args variable (build uses an arbitrary
#     # collection of unknown args for the make arguments)
#     args, unknown_args = parser.parse_known_args(sysargs)
#     args.unknown_args = unknown_args

    ####################
    # Version
    ####################
    if args.version:
        print(fmt("@{cf}CKX Tools@|: @{yf}" + pkg_resources.get_distribution('ckx_tools').version))
        print(fmt("@{cf}Python   @|: @{yf}" + ''.join(sys.version.split('\n'))))
        sys.exit(0)

    ####################
    # Colours
    ####################
    if args.test_colors:
        terminal_color.test_colors()
        sys.exit(0)
    if args.no_color or not args.force_color and not common.is_tty(sys.stdout):
        terminal_color.set_color(False)

    ####################
    # Execute
    ####################
    args = argument_preprocessors[args.verb](args)
    sys.exit(args.main(args) or 0)


def main(args=None):
    args = sys.argv[1:] if args is None else args
    try:
        ckx_main(args)
    except KeyboardInterrupt:
        print('Interrupted by user!')
