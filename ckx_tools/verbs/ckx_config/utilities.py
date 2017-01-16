# Copyright 2017 Daniel Stonier
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

##############################################################################
# Documentation
##############################################################################

"""
Supporting utilities to instantation cmake cache files, toolchains and
script launchers.
"""

##############################################################################
# Imports
##############################################################################

import os
import shutil
import stat  # file permissions

import ckx_tools.config

from . import color_console as console

##############################################################################
# Methods
##############################################################################

config_cache_filename = os.path.join(os.path.dirname(__file__), 'resources', 'cmake', 'config.cmake', )
overrides_filename = os.path.join(os.path.dirname(__file__), 'resources', 'cmake', 'overrides.cmake')

templates_home = os.path.join(os.path.dirname(__file__), 'resources', 'templates')
toolchains_home = os.path.join(os.path.dirname(__file__), 'resources', 'toolchains')
custom_toolchains_home = os.path.join(ckx_tools.config.home(), 'toolchains')
platforms_home = os.path.join(os.path.dirname(__file__), 'resources', 'platforms')
custom_platforms_home = os.path.join(ckx_tools.config.home(), 'platforms')


def file_to_string(filename):
    f = open(filename, 'r')
    try:
        t = f.read()
    finally:
        f.close()
    return t

def fill_in_session_scripts(template, name, cwd):
    return template % locals()

def instantiate_or_update_session_scripts(name, build_root_dir, workspace_dir):
    (_, _, filenames) = os.walk(templates_home).next()
    for filename in filenames:
        if not os.path.isfile(os.path.join(build_root_dir, filename)):
            raw_contents = file_to_string(os.path.join(templates_home, filename))
            contents = fill_in_session_scripts(raw_contents, name, workspace_dir)
            try:
                f = open(os.path.join(build_root_dir, filename), 'w')
                f.write(contents.encode('utf-8'))
            finally:
                os.fchmod(f.fileno(), stat.S_IRWXU | stat.S_IRWXG)
                f.close()

def fill_in_config_cmake(template, config_workspace, config_build_type, config_doc_prefix, config_underlays, config_override_file):
    return template % locals()

def instantiate_or_update_config_environment(
        name,
        workspace_dir,
        build_root_dir,
        platform,
        toolchain,
        doc_prefix,
        underlays
    ):
    """
    Instatiate if not already instatiated, or validate/update configuration
    files - scripts, cmake cache and if used, the toolchain module.

    :param str name: the build profile name
    :param str workspace_dir:
    :param str build_root_dir:
    :param str platform: unique identifier used to lookup the platform library
    :param str toolchain: unique identifier used to lookup the toolchain library
    :param str doc_prefix:
    :param list underlays: semi-colon separated list of underlay roots

    :raises RuntimeError: if it fails to setup anything
    """

    if not os.path.exists(build_root_dir):
        os.makedirs(build_root_dir)
    instantiate_or_update_session_scripts(
        name=os.path.basename(workspace_dir) + "_" + name,
        build_root_dir=build_root_dir,
        workspace_dir=workspace_dir
    )
    # this can throw a RuntimeError if the platform configuration is not found
    instantiate_or_update_config_cmake(
        platform,
        workspace_dir,
        build_root_dir,
        doc_prefix,
        underlays
    )
    # this can throw a RuntimeError if the toolchain is not found
    instantiate_or_udpate_toolchain_module(
        toolchain,
        build_root_dir
    )


def instantiate_or_update_config_cmake(platform_name, workspace_dir, build_root_dir, config_doc_prefix, config_underlays):
    '''
    Copy the cache configuration template to the build path.

    :param platform_name: name of the platform configuration to bring to the cache
    :param build_root_dir: location of the build directory to save the config.cmake file.

    :raises RuntimeError: if it fails to setup anything
    '''
    # this one can throw a RuntimeError
    platform_content = get_platform_content(platform_name)
    config_build_type = "RelWithDebInfo"
    if os.path.isfile(os.path.join(build_root_dir, 'config.cmake')):
        # TODO : validate an existing cache file to make sure it hasn't been unintentially put in a conflicting state by the user
        return
    raw_content = file_to_string(config_cache_filename)
    contents = fill_in_config_cmake(raw_content, workspace_dir, config_build_type, config_doc_prefix, config_underlays, overrides_filename)
    config_cmake_file = os.path.join(build_root_dir, "config.cmake")
    try:
        f = open(config_cmake_file, 'w')
        f.write(platform_content.encode('utf-8'))
        f.write(contents.encode('utf-8'))
    finally:
        f.close()

def instantiate_or_udpate_toolchain_module(toolchain, build_root_dir):
    """
    Instantate with a toolchain module, or remove/replace it if the configuration
    is different to the file that is present.

    :param str toolchain: string identifier representing a toolchain in the library
    :param str build_root_dir:

    :raises RuntimeError: if it can't find the toolchain module in the library
    """
    if toolchain:
        # TODO assert the file is there and the right toolchain and if not, proceed
        tmp_list = toolchain.split('/')
        if len(tmp_list) != 2:
            raise RuntimeError("Toolchain specification invalid, must be <family>/<tuple> [%s]" % toolchain)
        family = tmp_list[0]
        toolchain_tuple = tmp_list[1]
        toolchains = get_toolchains_or_platforms(toolchains_home)
        custom_toolchains = get_toolchains_or_platforms(custom_toolchains_home)
        if family not in toolchains and family not in custom_toolchains:
            raise RuntimeError("No toolchains available for family %s" % family)
        if family in custom_toolchains and toolchain_tuple in custom_toolchains[family]:
            toolchain_file = os.path.join(custom_toolchains_home, family, toolchain_tuple + ".cmake")
        elif family in toolchains and toolchain_tuple in toolchains[family]:
            toolchain_file = os.path.join(toolchains_home, family, toolchain_tuple + ".cmake")
        else:
            raise RuntimeError("Platform %s for family %s not available." % (family, toolchain_tuple))
        if os.path.isfile(toolchain_file):
            shutil.copy(toolchain_file, os.path.join(build_root_dir, "toolchain.cmake"))
        else:
            raise RuntimeError("Toolchain module not available [%s]" % toolchain_file)
    else:
        toolchain_filename = os.path.join(build_root_dir, "toolchain.cmake")
        if os.path.isfile(toolchain_filename):
            os.remove(toolchain_filename)


def get_toolchains_or_platforms(base_path):
    '''
      Does a look up in the path for either toolchain or platform files.
      @param base_path : start of the search (ends in either toolchains or platforms).
    '''
    d = {}
    for (dirpath, unused_dirname, filenames) in os.walk(base_path):
        if dirpath != base_path:  # skip the root, only find files in subfolders
            family = os.path.basename(dirpath)
            d[family] = []
            for filename in filenames:
                d[family].append(os.path.splitext(filename)[0])  # leave off the .cmake extension
    return d

def get_platform_content(platform_name):
    """
    Retrieve cmake platform configuration from the library.

    :raises RuntimeError: if it can't find the platform configuration file.
    """
    platform_content = ""
    if platform_name:
        tmp_list = platform_name.split('/')
        if len(tmp_list) != 2:
            raise RuntimeError("Platform specification invalid, must be <family>/<platform type> [%s]" % platform_name)
        family = tmp_list[0]
        platform = tmp_list[1]
        platforms = get_toolchains_or_platforms(platforms_home)
        custom_platforms = get_toolchains_or_platforms(custom_platforms_home)
        if family not in platforms and family not in custom_platforms:
            raise RuntimeError("No platforms available for family %s" % family)
        if family in custom_platforms and platform in custom_platforms[family]:
            platform_file = os.path.join(custom_platforms_home, family, platform + ".cmake")
        elif family in platforms and platform in platforms[family]:
            platform_file = os.path.join(platforms_home, family, platform + ".cmake")
        else:
            raise RuntimeError("platform %s for family %s not available." % (family, platform))
    else:
        platform_file = os.path.join(platforms_home, 'default.cmake')

    if os.path.isfile(platform_file):
        f = open(platform_file, 'r')
        try:
            platform_content = f.read()
        finally:
            f.close()
    else:
        raise RuntimeError("platform configuration not available [%s]" % platform_file)
    return platform_content

def list_toolchains():
    console.pretty_println("\n******************************** Toolchain List **********************************", console.bold)
    toolchains = get_toolchains_or_platforms(toolchains_home)
    print(console.bold + "Official " + console.reset + "({0})".format(toolchains_home))
    for family in toolchains:
        for platform in toolchains[family]:
            console.pretty_print(" -- %s/" % family, console.cyan)
            console.pretty_println("%s" % platform, console.yellow)
    print(console.bold + "Custom " + console.reset + "({0})".format(custom_toolchains_home))
    toolchains = get_toolchains_or_platforms(custom_toolchains_home)
    if toolchains:
        for family in toolchains:
            for platform in toolchains[family]:
                console.pretty_print(" -- %s/" % family, console.cyan)
                console.pretty_println("%s" % platform, console.yellow)
    else:
        console.pretty_println(" -- ", console.cyan)
    console.pretty_println("**********************************************************************************\n", console.bold)


def list_platforms():
    console.pretty_println("\n********************************* Platform List **********************************", console.bold)
    platforms = get_toolchains_or_platforms(platforms_home)
    print(console.bold + "Official " + console.reset + "({0})".format(platforms_home))
    for family in platforms:
        for platform in platforms[family]:
            console.pretty_print(" -- %s/" % family, console.cyan)
            console.pretty_println("%s" % platform, console.yellow)
    print(console.bold + "Custom " + console.reset + "({0})".format(custom_platforms_home))
    platforms = get_toolchains_or_platforms(custom_platforms_home)
    if platforms:
        for family in platforms:
            for platform in platforms[family]:
                console.pretty_print(" -- %s/" % family, console.cyan)
                console.pretty_println("%s" % platform, console.yellow)
    else:
        console.pretty_println(" -- ", console.cyan)
    console.pretty_println("**********************************************************************************\n", console.bold)

