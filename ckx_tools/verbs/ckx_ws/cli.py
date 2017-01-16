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

import argparse
import ckx_tools.common as common
import ckx_tools.config as config
import ckx_tools.argument_parsing as argument_parsing
import ckx_tools.metadata as metadata
import os
import sys
import urllib2
import urlparse
import yaml

from ckx_tools.context import Context
from ckx_tools.terminal_color import ColorMapper
color_mapper = ColorMapper()
clr = color_mapper.clr

##############################################################################
# Import checks
##############################################################################

try:
    import wstool.wstool_cli
except ImportError:
    sys.exit("\nThe workspace tool is not installed: 'sudo apt-get install python-wstool'\n")

##############################################################################
# Entry Point API
##############################################################################


def help_string():
    overview = 'Creates and populates catkin workspaces.\n\n'
    instructions = "Usage:\n\n  \
Empty Workspace:\n  \
 - 'ckx ws ecl' : create an empty workspace in ./ecl.\n  \
 - 'ckx ws ~/ecl' : create an empty workspace in ~/ecl.\n  \
From Rosinstall:\n  \
 - 'ckx ws ecl ecl.rosinstall' : populate a workspace from rosinstall file.\n  \
 - 'ckx ws ecl https://raw.github.com/stonier/ecl_core/devel/ecl.rosinstall' : populate from uri.\n  \
From Rosinstall Database:\n  \
 - 'ckx ws ecl ecl' : populate a workspace from our rosinstall database from the default track.\n  \
 - 'ckx ws --track=kinetic ecl ecl' : populate a workspace from the current rosinstall database for kinetic.\n  \
 - 'ckx ws --merge ./ecl_extras.rosinstall' : merge sources from another rosinstall.\n  \
Management:\n  \
 - 'ckx ws --clean' : clean metadata produced by 'ckx config', 'ckx build' from the workspace.\n  \
Configuration:\n  \
 - 'ckx settings --get-default-track' : shows the currently set default track.\n  \
 - 'ckx settings --set-default-track=kinetic' : sets the currently set default track.\n  \
 - 'ckx ws --get-rosinstall-database-uri' : return the currently configured rosinstall database uri.\n  \
 - 'ckx ws --set-rosinstall-database-uri' : save this url as the default rosinstall database uri.\
 "
    return overview + instructions


def prepare_arguments(parser):
    default_track = common.get_default_track()

    parser.epilog = help_string()
    add = parser.add_argument
    add('dir', nargs='?', default=os.getcwd(), help='directory to use for the workspace [cwd]')
    add('--track', action='store', default=default_track, help='retrieve rosinstalls relevant to this track %s [%s]' % (common.VALID_TRACKS, default_track))
    add('-m', '--merge', action='store', default=None, help='merge a keyed (--list-rosinstall) rosinstall into the current workspace')
    add('-j', '--jobs', action='store', default=1, help='how many parallel threads to use for installing[1]')
    add('uri', nargs=argparse.REMAINDER, default=None, help='uri for a rosinstall file [None]')

    management_group = parser.add_argument_group('Management', 'options to assist in managing your workspace')
    add = management_group.add_argument
    add('--clean', action='store_true', default=False,
        help='Clean build metadata for the given workspace (does not touch rosinstalled sources).')

    configuration_group = parser.add_argument_group('Configuration', 'Options to assist in configuring this tool')
    add = configuration_group.add_argument
    add('--list-rosinstalls', action='store_true', help='list all currently available rosinstalls [false]')
    parser.add_argument('--get-rosinstall-database-uri', action='store_true', help='print the default rosinstall database uri')
    parser.add_argument('--set-rosinstall-database-uri', action='store', default=None, help='set a new default  rosinstall database uri')

    return parser

def main(opts):
    '''
      Process the workspace command and return success or failure to the calling script.
    '''

    ########################################
    # Rosinstall Database Management
    ########################################
    if opts.get_rosinstall_database_uri:
        print get_rosinstall_database_uri()
        return 0
    if opts.set_rosinstall_database_uri:
        print(clr("\n@{cf}New Rosinstall Database Uri:@| @{yf}{0}@|\n").format(set_rosinstall_database_uri(opts.set_rosinstall_database_uri)))
        return 0
    if opts.list_rosinstalls:
        list_rosinstalls(opts.track)
        return 0

    ########################################
    # Clean all build/profile information
    ########################################
    workspace_dir = opts.dir if os.path.isabs(opts.dir) else os.path.join(os.getcwd(), opts.dir)
    if opts.clean:
        profile_names = metadata.get_profile_names(workspace_dir)
        for name in profile_names:
            metadata.remove_profile(workspace_dir, name)
        metadata.init_metadata_root(
            workspace_path=workspace_dir,
            reset=True)
        return 0

    ########################################
    # Check/Init a Workspace
    ########################################
    initialised_new_workspace = False
    sources_dir = os.path.join(workspace_dir, 'src')
    try:
        # Try to load an existing context
        ctx = Context.load(workspace_dir, strict=True)

        # Initialize a new context if necessary
        if not ctx:
            print('Initializing catkin workspace in `%s`.' % (workspace_dir or os.getcwd()))
            if not os.path.isdir(workspace_dir):
                os.mkdir(workspace_dir)
            # Init the metadata
            metadata.init_metadata_root(
                workspace_path=workspace_dir or os.getcwd(),
                reset=False)
            ctx = Context.load(workspace_dir)

            init_sources(sources_dir)
            initialised_new_workspace = True
        else:
            print('[ws] catkin workspace `%s` found.' % (ctx.workspace))
        # print(ctx.summary())

    except IOError as exc:
        # Usually happens if workspace is already underneath another ckx_tools workspace
        print(clr("[ws] @!@{rf}Error:@| could not init/introspect the workspace (it's nested under another?): `%s`" % exc.message))
        return 1

    ####################
    # Rosinstalls
    ####################
    uri_list = []
    lookup_name_list = []
    lookup_database = None
    if opts.uri:
        # parse the list looking for 1) abs 2) rel 3) lookup names, 4) http uri's
        for uri in opts.uri:
            if os.path.isabs(uri):
                uri_list.append(uri)
            elif os.path.isfile(os.path.join(os.getcwd(), uri)):
                uri_list.append(os.path.join(os.getcwd(), uri))
            elif urlparse.urlparse(uri).scheme == "":  # not a http element, let's look up our database
                lookup_name_list.append(uri)
            else:  # it's a http element'
                uri_list.append(uri)
        # lookup the database and convert to http uri's if necessary
        if lookup_name_list:
            try:
                rosinstall_database, lookup_database = get_rosinstall_database(opts.track)
            except RuntimeError as exc:
                print(clr("[ws] @!@{rf}Error: %s@|" % str(exc)))
                return 1
            (database_name_list, database_uri_list) = parse_database(lookup_name_list, rosinstall_database)
            lookup_name_list.extend(database_name_list)
            uri_list.extend(database_uri_list)
        populate_sources(sources_dir, uri_list, opts.jobs)
        print_details(workspace_dir,
                      uri_list,
                      lookup_name_list,
                      opts.track,
                      lookup_database,
                      initialised_new_workspace
                      )
    elif initialised_new_workspace:
        print_banner("Initialised Empty Workspace")
        print(clr("@{cf}Workspace  : @|@{yf}{0}@|").format(workspace_dir))
        print_footer()
        print_proceed()
    else:
        print_banner("Workspace Details")
        print(clr("@{cf}Workspace  : @|@{yf}{0}@|").format(workspace_dir))
        print_footer()

    return 0

##############################################################################
# Settings
##############################################################################

DEFAULT_ROSINSTALL_DATABASE = 'https://raw.github.com/stonier/ckx_tools/rosinstalls'

def get_rosinstall_database_uri():
    filename = os.path.join(config.home(), "rosinstall_database")
    try:
        f = open(filename, 'r')
    except IOError:
        return set_rosinstall_database_uri()
    rosinstall_database = f.read()
    f.close()
    return rosinstall_database

def set_rosinstall_database_uri(rosinstall_database=DEFAULT_ROSINSTALL_DATABASE):
    '''
      Set a uri for your rosinstall database.
    '''
    # could actually check that it is a valid uri though.
    filename = os.path.join(config.home(), "rosinstall_database")
    f = open(filename, 'w+')
    try:
        f.write(rosinstall_database.encode('utf-8'))
    finally:
        f.close()
    return rosinstall_database

##############################################################################
# Helpers
##############################################################################

def init_sources(base_path):
    """
    Init an empty wstools source workspace.

    :param str base_path: location of the wstool workspace
    """
    wstool_arguments = ['wstool',
                        'init',
                        base_path,
                        ]
    wstool.wstool_cli.wstool_main(wstool_arguments)

def populate_sources(base_path, uri_list, parallel_jobs):
    '''
      :param str base_path: location of the wstool workspace
      :param uri_list: list of uri's to rosinstall files
      :type uri_list: list of str
    '''
    for uri in uri_list:
        wstool_arguments = ['wstool',
                            'merge',
                            '--target-workspace=%s' % base_path
                            ]
        wstool_arguments.append(uri)
        wstool.wstool_cli.wstool_main(wstool_arguments)
    # update
    wstool_arguments = ['wstool',
                        'update',
                        '-j %s' % str(parallel_jobs),
                        '--target-workspace=%s' % base_path
                        ]
    wstool.wstool_cli.wstool_main(wstool_arguments)

def list_rosinstalls(track):
    if not track:
        track = common.get_default_track()
    rosinstall_database_uri = '%s/%s.yaml' % (get_rosinstall_database_uri(), track)
    try:
        response = urllib2.urlopen(rosinstall_database_uri)
    except urllib2.URLError as unused_e:
        raise urllib2.URLError("rosinstall database uri not found [{0}]".format(rosinstall_database_uri))
    rosinstalls = yaml.load(response.read())
    sorted_rosinstalls = rosinstalls.keys()
    sorted_rosinstalls.sort()
    for r in sorted_rosinstalls:
        print(clr("@{cf} " + r + ": @|@{yf}{0}@|").format(rosinstalls[r]))


def get_rosinstall_database(track):
    lookup_database = get_rosinstall_database_uri()
    rosinstall_database_uri = '%s/%s.yaml' % (lookup_database, track)
    try:
        unused_response = urllib2.urlopen(rosinstall_database_uri)
    except urllib2.URLError as unused_e:
        raise RuntimeError("rosinstall database uri not found [{0}]".format(rosinstall_database_uri))
    response = urllib2.urlopen('%s/%s.yaml' % (lookup_database, track))
    rosinstall_database = yaml.load(response.read())
    return rosinstall_database, lookup_database


def parse_database(search_names, rosinstall_database):
    names = []
    sources = []
    for name in search_names:
        if name in rosinstall_database:
            elements = rosinstall_database[name]
            new_names = []
            new_sources = []
            if type(elements) is list:
                for element in elements:
                    if element.endswith('.rosinstall'):
                        new_sources.append(element)
                    else:
                        new_names.append(element)
            else:  # single entry
                if elements.endswith('.rosinstall'):
                    new_sources.append(elements)
                else:
                    new_names.append(elements)
            names.extend(new_names)
            sources.extend(new_sources)
            if new_names:
                (new_names, new_sources) = parse_database(new_names, rosinstall_database)
                names.extend(new_names)
                sources.extend(new_sources)
        else:
            raise RuntimeError("not found in the rosinstall database [%s]" % name)
#                    (new_names, new_sources) = parse_database([elements], rosinstall_database)
#                        (new_names, new_sources) = parse_database([element], rosinstall_database)
#                        names.extend(new_names)
#                        sources.extend(new_sources)
#                    sources.append(elements)
#                    names.extend(new_names)
#                    sources.extend(new_sources)
    return (names, sources)

##############################################################################
# Printers
##############################################################################

def print_banner(title):
    width = 80
    print(clr("@!\n" + "*" * width + "@|"))
    print(clr("@!{text:^{width}}".format(text=title, width=width) + "@|"))
    print(clr("@!*" * width + "@|"))

def print_footer():
    width = 80
    print(clr("@!*" * width + "\n" + "@|"))

def print_details(workspace_dir, uri_list, lookup_name_list, lookup_track, lookup_database, initialised_new_workspace):
    if initialised_new_workspace:
        print_banner("Initialised Workspace")
    else:
        print_banner("Updated Workspace")
    print(clr("@{cf}Workspace  : @|@{yf}" + workspace_dir + "@|"))
    if lookup_name_list:
        s = "@{cf}Keys       : @|@{yf}"
        for lookup_name in lookup_name_list:
            s += "%s " % lookup_name
        s += "@|"
        print(clr(s))
        print(clr("@{cf}Track      : @|@{yf}" + lookup_track + "@|"))
        print(clr("@{cf}Database   : @|@{yf}" + lookup_database + "@|"))
    if uri_list:
        print(clr("@{cf}Rosisntalls: @|@{yf}%s@|" % uri_list[0]))
        for uri in uri_list[1:]:
            print(clr("@{cf}           : @|@{yf}%s@|" % uri))
    print_footer()
    if initialised_new_workspace:
        print_proceed()

def print_proceed():
    print(clr("@{cf}Proceed to configure parallel builds with 'ckx config'.@|\n"))


