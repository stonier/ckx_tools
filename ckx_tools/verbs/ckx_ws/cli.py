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
import ckx_tools.metadata as metadata
import os
import sys
import urllib2
import urlparse
import vci
import vcstool.commands.import_
import vcstool.executor
import yaml

from ckx_tools.context import Context
from ckx_tools.terminal_color import ColorMapper
color_mapper = ColorMapper()
clr = color_mapper.clr

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
 - 'ckx ws ecl ecl.repos' : populate a workspace from a .repos file.\n  \
 - 'ckx ws ecl https://raw.github.com/stonier/ecl_core/devel/ecl.repos' : populate from url.\n  \
From Rosinstall Database:\n  \
 - 'ckx ws ecl ecl' : populate a workspace from the currently set version control index.\n  \
 - 'ckx ws --merge ./ecl_extras.repos' : merge sources from another .repos installer.\n  \
Management:\n  \
 - 'ckx ws --clean' : clean metadata produced by 'ckx config', 'ckx build' from the workspace.\n  \
Configuration:\n  \
 - 'ckx ws --get-vci-url' : return the currently configured version control index url.\n  \
 - 'ckx ws --set-vci-url' : save this url as the default version control index url.\
 "
    return overview + instructions


def prepare_arguments(parser):
    parser.epilog = help_string()
    add = parser.add_argument
    add('dir', nargs='?', default=os.getcwd(), help='directory to use for the workspace [cwd]')
    add('-j', '--jobs', action='store', default=10, help='how many parallel threads to use for installing [10]')
    add('uri', nargs=argparse.REMAINDER, default=None, help='uri for a rosinstall file [None]')

    management_group = parser.add_argument_group('Management', 'options to assist in managing your workspace')
    add = management_group.add_argument
    add('--clean', action='store_true', default=False,
        help='Clean build metadata for the given workspace (does not touch rosinstalled sources).')

    configuration_group = parser.add_argument_group('Configuration', 'Options to assist in configuring this tool')
    add = configuration_group.add_argument
    add('--list', action='store_true', help='list all currently available repos in the index [false]')
    parser.add_argument('--get-vci-url', action='store_true', help='print the default rosinstall database uri')
    parser.add_argument('--set-vci-url', action='store', default=None, help='set a new default  rosinstall database uri')

    return parser


def main(opts):
    '''
      Process the workspace command and return success or failure to the calling script.
    '''

    ########################################
    # Version Control Index Management
    ########################################
    if opts.get_vci_url:
        print(clr("\n@{cf}URL @|: @{yf}{0}@|\n").format(vci.config.get_index_url()))
        return 0
    if opts.set_vci_url:
        vci.config.set_index_url(opts.set_vci_url)
        print(clr("\n@{cf}URL @|: @{yf}{0}@|\n").format(opts.set_vci_url))
        return 0
    if opts.list:
        url = vci.config.get_index_url()
        try:
            contents = vci.index_contents.get(url)
        except urllib2.URLError as e:
            print(clr("\n@{rf}[ERROR] could not retrieve {0}@|").format(str(e)))
            sys.exit(1)
        vci.index_contents.display(url, contents)
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
            os.mkdir(sources_dir)
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
    file_list = []
    uri_list = []
    lookup_name_list = []
    lookup_index_url = vci.config.get_index_url()
    if opts.uri:
        # parse the list looking for 1) abs 2) rel 3) lookup names, 4) http uri's
        for uri in opts.uri:
            if os.path.isabs(uri):
                file_list.append(uri)
            elif os.path.isfile(os.path.join(os.getcwd(), uri)):
                file_list.append(os.path.join(os.getcwd(), uri))
            elif urlparse.urlparse(uri).scheme == "":  # not a http element, let's look up our database
                lookup_name_list.append(uri)
            else:  # it's a http element'
                uri_list.append(uri)
#         # lookup the database and convert to http uri's if necessary
#         if lookup_name_list:
#             try:
#                 rosinstall_database, lookup_database = get_rosinstall_database(opts.track)
#             except RuntimeError as exc:
#                 print(clr("[ws] @!@{rf}Error: %s@|" % str(exc)))
#                 return 1
#             (database_name_list, database_uri_list) = parse_database(lookup_name_list, rosinstall_database)
#             lookup_name_list.extend(database_name_list)
#             uri_list.extend(database_uri_list)
        populate_sources(sources_dir, file_list, uri_list, lookup_name_list, opts.jobs)
        print_details(workspace_dir,
                      file_list,
                      uri_list,
                      lookup_name_list,
                      lookup_index_url,
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


def _execute_vci(args):
    """
    :param [str] args: list of args to pass to vci
    """

##############################################################################
# Helpers
##############################################################################


class Args(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """
    def __init__(self, *args, **kwargs):
        super(Args, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Args, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Args, self).__delitem__(key)
        del self.__dict__[key]


def populate_sources(base_path, file_list, uri_list, lookup_name_list, parallel_jobs):
    '''
      :param str base_path: location of the vcstool workspace
      :param str file_list: list of files to setup
      :param str uri_list: list of url's to setup
      :param str lookup_name_list: list of vci keys to lookup and setup
      :param int parallel_jobs: faster, faster
    '''
    combined_yaml_contents = {'repositories': {}}
    if uri_list:
        print("@{yf}[WARN] populating from uri's is not supported at this time@|")
    for filename in file_list:
        print("Populating from filename {0}".format(filename))
        with open(filename, 'r') as stream:
            try:
                new_yaml_contents = yaml.load(stream)
                combined_yaml_contents['repositories'].update(new_yaml_contents['repositories'])
            except yaml.YAMLError as e:
                print(clr("@{yf}[WARN] could not open '{0}', skipping [{1}]@|").format(filename, str(e)))
    if lookup_name_list:
        print("Populating from lookup names {0}".format(lookup_name_list))
        new_yaml_contents = vci.find.create_yaml_from_key(lookup_name_list)
        combined_yaml_contents['repositories'].update(new_yaml_contents['repositories'])

    # the vcstool way (alternative : subprocess it)
    args = Args({'path': base_path, 'debug': False, 'workers': parallel_jobs, 'repos': True})
    repos = vcstool.commands.import_.get_repos_in_vcstool_format(combined_yaml_contents['repositories'])
    jobs = vcstool.commands.import_.generate_jobs(repos, args)  # need to wire up a special args here
    results = vcstool.executor.execute_jobs(jobs, show_progress=True, number_of_workers=parallel_jobs, debug_jobs=False)
    vcstool.executor.output_results(results)

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


def print_details(workspace_dir, file_list, uri_list, lookup_name_list, lookup_index_url, initialised_new_workspace):
    if initialised_new_workspace:
        print_banner("Initialised Workspace")
    else:
        print_banner("Updated Workspace")
    print(clr("@{cf}Workspace  : @|@{yf}" + workspace_dir + "@|"))
    if lookup_name_list:
        print(clr("@{cf}VCI Url    : @|@{yf}" + lookup_index_url + "@|"))
        s = "@{cf}VCI Keys   : @|@{yf}"
        for lookup_name in lookup_name_list:
            s += "%s " % lookup_name
        s += "@|"
        print(clr(s))
    if file_list:
        print(clr("@{cf}Files      : @|@{yf}%s@|" % file_list[0]))
        for filename in file_list[1:]:
            print(clr("@{cf}           : @|@{yf}%s@|" % filename))
    if uri_list:
        print(clr("@{cf}Rosisntalls: @|@{yf}%s@|" % uri_list[0]))
        for uri in uri_list[1:]:
            print(clr("@{cf}           : @|@{yf}%s@|" % uri))
    print_footer()
    if initialised_new_workspace:
        print_proceed()


def print_proceed():
    print(clr("@{cf}Proceed to configure parallel builds with 'ckx config'.@|\n"))
