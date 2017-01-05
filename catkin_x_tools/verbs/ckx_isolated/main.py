#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/stonier/ckx_tools/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Implementation of the 'ckx isolated' verb.
"""

##############################################################################
# Imports
##############################################################################


##############################################################################
# Methods
##############################################################################


def help_string():
    overview = 'Builds packages in a catkin workspace in isolation.\n\n'
    instructions = " \
 - 'ckx isolated' : build all catkin/cmake projects in isolation\n \
 "
    return overview + instructions


def prepare_arguments(parser):
    parser.description = help_string()
    parser.add_argument('--merge', action='store_true', default=False, help='Build each catkin package into a common devel space.')
    parser.add_argument('-j', '--jobs', type=int, metavar='JOBS', nargs='?', default=None, help='Specifies the number of jobs (commands) to run simultaneously. Defaults to the environment variable ROS_PARALLEL_JOBS and falls back to the number of CPU cores.')
    parser.add_argument('-i', '--install', action='store_true', default=False, help='Run install step after making [false]')
    parser.add_argument('--strip', action='store_true', help='Strips binaries, only valid with --install')
    parser.add_argument('--force-cmake', action='store_true', default=False, help='Invoke "cmake" even if it has been executed before [false]')
    parser.add_argument('--no-color', action='store_true', help='Disables colored ouput')
    parser.add_argument('--target', default=None, help='Build against a particular target only')
    parser.add_argument('--pkg', nargs='+', metavar='PKGNAME', dest='packages', help='Invoke "make" on specific packages (only after initial invocation)')
    parser.add_argument('-s', '--suffixes', action='store_true', default=False, help='Add _isolated to build/install paths.')
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='Suppresses the cmake and make output until an error occurs.')
    parser.add_argument('-p', '--pre-clean', action='store_true', help='Clean build temporaries before making [false]')
    parser.add_argument('--cmake-args', dest='cmake_args', nargs='*', type=str, help='Arguments to be passed to CMake.')
    parser.add_argument('--make-args', dest='make_args', nargs='*', type=str, help='Arguments to be passed to make.')
    return parser

def main(args):
    print("UNSUPPORTED")
    return 0
