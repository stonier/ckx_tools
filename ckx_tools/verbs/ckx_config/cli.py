# Copyright 2014 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import os

import ckx_tools.metadata as metadata

from ckx_tools.argument_parsing import add_cmake_and_make_and_catkin_make_args
from ckx_tools.argument_parsing import add_context_args

from ckx_tools.context import Context

from ckx_tools.terminal_color import ColorMapper
from audioop import cross

from . import utilities

color_mapper = ColorMapper()
clr = color_mapper.clr


def prepare_arguments(parser):

    parser.description = "This verb is used to configure a catkin workspace's\
    configuration and layout. Calling `catkin config` with no arguments will\
    display the current config and affect no changes if a config already exists\
    for the current workspace and profile."

    # Workspace / profile args
    add_context_args(parser)

    common_group = parser.add_argument_group('Common Options', 'Most frequently used options.')
    # add = common_group.add_argument
    add = common_group.add_mutually_exclusive_group().add_argument
    add('--underlays', '-u', dest='underlays', type=str, default=None,
        help='Explicitly extend the result-space of other catkin workspace underlays, '
        'overriding the value of $CMAKE_PREFIX_PATH.')
    add('--no-underlays', dest='underlays', action='store_const', const='',
        help="Clear any setting previously created by '--underlays'")
    add('-i', '--install-space', default=None,
        help="Sets the target install space ['{0}']".format(Context.DEFAULT_INSTALL_SPACE))
    add('--install', action='store_true', default=None,
        help='Enables the installation step')
    add('--no-install', dest='install', action='store_false', default=None,
        help='Disables the installation step')
    add = common_group.add_mutually_exclusive_group().add_argument
    add('--whitelist', metavar="PKG", dest='whitelist', nargs="+", required=False, type=str, default=None,
        help='Set the packages on the whitelist. If the whitelist is non-empty, '
        'only the packages on the whitelist are built with a bare call to '
        '`catkin build`.')
    add('--no-whitelist', dest='whitelist', action='store_const', const=[], default=None,
        help='Clear all packages from the whitelist.')
    add = common_group.add_mutually_exclusive_group().add_argument
    add('--blacklist', metavar="PKG", dest='blacklist', nargs="+", required=False, type=str, default=None,
        help='Set the packages on the blacklist. Packages on the blacklist are '
        'not built with a bare call to `catkin build`.')
    add('--no-blacklist', dest='blacklist', action='store_const', const=[], default=None,
        help='Clear all packages from the blacklist.')
    add('--init', action='store_true', default=False,
        help='Initialize a workspace if it does not yet exist.')

    spaces_group = parser.add_argument_group('Advanced Space Configuration', 'Location of parts of the catkin workspace.')
    add = spaces_group.add_argument
    add('-s', '--source-space', default=Context.DEFAULT_SOURCE_SPACE,
        help="The path to the source space ['{0}']".format(Context.DEFAULT_SOURCE_SPACE))
    add('-l', '--log-space', default=None,
        help="The path to the log space ['{0}']".format(Context.DEFAULT_LOG_SPACE))
    add('-b', '--build-space', default=None,
        help="The path to the build space ['{0}']".format(Context.DEFAULT_BUILD_SPACE))
    add('-d', '--devel-space', default=None,
        help="Sets the target devel space ['{0}']".format(Context.DEFAULT_DEVEL_SPACE))

    devel_group = parser.add_argument_group(
        'Advanced Devel Configuration', 'Options for configuring the structure of the devel space.')
    add = devel_group.add_mutually_exclusive_group().add_argument
    add('--link-devel', dest='devel_layout', action='store_const', const='linked', default=None,
        help='Build products from each catkin package into isolated spaces,'
        ' then symbolically link them into a merged devel space.')
    add('--merge-devel', dest='devel_layout', action='store_const', const='merged', default=None,
        help='Build products from each catkin package into a single merged devel spaces.')
    add('--isolate-devel', dest='devel_layout', action='store_const', const='isolated', default=None,
        help='Build products from each catkin package into isolated devel spaces.')

    install_group = parser.add_argument_group(
        'Advanced Install Configuration', 'Options for configuring the structure of the install space.')
    add = install_group.add_mutually_exclusive_group().add_argument
    add('--isolate-install', action='store_true', default=None,
        help='Each package to a separate install space.')
    add('--merge-install', dest='isolate_install', action='store_false', default=None,
        help='Each package to a single merged install space [default].')

    build_group = parser.add_argument_group('Advanced Build Options', 'Options for configuring the way packages are built.')
    add_cmake_and_make_and_catkin_make_args(build_group)

    cross_compiling_group = parser.add_argument_group('Cross Compiling', 'Options for configuring a cross compiling environment.')
    add = cross_compiling_group.add_argument
    add('--list-toolchains', action='store_true', help='list all currently available toolchain modules [false]')
    add('--list-platforms', action='store_true', help='list all currently available platform modules [false]')
    add('--toolchain', action='store', default=None, help='toolchain cmake module to load []')
    add('--platform', action='store', default=None, help='platform cmake cache module to load [default]')

    behavior_group = parser.add_argument_group('Argument handling', 'Options affecting argument handling.')
    add = behavior_group.add_mutually_exclusive_group().add_argument
    add('--append-args', '-a', action='store_true', default=False,
        help='For list-type arguments, append elements.')
    add('--remove-args', '-r', action='store_true', default=False,
        help='For list-type arguments, remove elements.')

    return parser

def main(opts):
    try:
        # Determine if the user is trying to perform some action, in which
        # case, the workspace should be automatically initialized
        ignored_opts = ['main', 'verb']
        actions = [v for k, v in vars(opts).items() if k not in ignored_opts]
        no_action = not any(actions)

        # Generic display functions only
        # List toolchains or platforms
        if opts.list_toolchains:
            utilities.list_toolchains()
            return 0
        if opts.list_platforms:
            utilities.list_platforms()
            return 0

        # Try to find a metadata directory to get context defaults
        # Otherwise use the specified directory
        context = Context.load(
            opts.workspace,
            opts.profile,
            opts,
            append=opts.append_args,
            remove=opts.remove_args)

        do_init = opts.init or not no_action
        summary_notes = []

        if not context.initialized() and do_init:
            summary_notes.append(clr('@!@{cf}Initialized new catkin workspace in `%s`@|' % context.workspace))

        if context.initialized() or do_init:
            Context.save(context)
            try:
                config_doc_prefix = ""
                utilities.instantiate_or_update_config_environment(
                    context.profile,
                    context.workspace,
                    context.build_root_abs,
                    context.platform,
                    context.toolchain,
                    config_doc_prefix,
                    context.underlays
                )
            except RuntimeError as e:
                print(clr("[config] @!@{rf}Error:@| %s") % e.message)
                return 1

        if not context.source_space_exists():
            os.makedirs(context.source_space_abs)

        print(context.summary(notes=summary_notes))

    except IOError as e:
        # Usually happens if workspace is already underneath another ckx_tools workspace
        print(clr("[config] @!@{rf}Error:@| could not configure catkin workspace: `%s`") % e.message)
        return 1

    return 0
