#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/stonier/ckx_tools/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Implementation of the 'ckx rosdoc' verb.
"""

##############################################################################
# Imports
##############################################################################

import os
import subprocess

import catkin_pkg.packages as catkin_packages
import catkin_tools.argument_parsing as argument_parsing
import catkin_tools.common as common
import catkin_tools.metadata as metadata

from catkin_tools.context import Context
from catkin_tools.terminal_color import ColorMapper
from catkin_tools.utils import which

from . import templates

color_mapper = ColorMapper()
clr = color_mapper.clr

##############################################################################
# Entry Point API
##############################################################################

def help_string():
    instructions = clr("@!Examples@|\n\n  \
@{gf}Minimal Use Cases@|\n\n  \
  @{cf}ckx rosdep --install@| : @{yf}install rosdeps for the active profile in the enclosing workspace@|\n  \
  @{cf}ckx rosdep --list@|    : @{yf}list all rosdep keys for the active profile in the enclosing workspace@|\n\n  \
@{gf}Targeted Profile or Workspace@|\n\n  \
  @{cf}ckx rosdep --workspace ~/foo_ws --install@| : @{yf}install rosdeps for the active profile in the specified workspace@|\n  \
  @{cf}ckx rosdep --profile native --install@| : @{yf}install rosdeps for the specified profile in the enclosing workspace@|\n  \
 ")
    return instructions

def prepare_arguments(parser):
    parser.epilog = help_string()
    argument_parsing.add_context_args(parser) # workspace / profile args
    add = parser.add_argument
    add('packages', nargs='*', help="workspace packages to doc, if none are given, then all are generated")
    return parser


def main(opts):
    # Do we have rosdoc_lite?
    if not which(DOC_PROGRAM):
        print(clr("[rosdoc] @!@{rf}Error: {0}' is not available.@|").format(DOC_PROGRAM))
        print(clr("[rosdoc] @!@{rf}Error: please make sure '{0}' is installed and in your path@|").format(DOC_PROGRAM))
        return 1

    # Are we in a parallel build profile? If so, prefer that over the active one
    if not opts.profile:
        enclosing_profile = metadata.find_enclosing_profile(os.getcwdu(), opts.workspace)
        if enclosing_profile:
            print(clr("@!\nInfo: in a parallel build folder, prefer this profile [%s]\n@|" % enclosing_profile))
            opts.profile = enclosing_profile

    # Load the context
    context = Context.load(opts.workspace, opts.profile, opts)

    if not os.path.exists(context.doc_space_abs):
        os.mkdir(context.doc_space_abs)

    # List of packages, curtail if restricted list is specified
    packages = catkin_packages.find_packages(context.source_space_abs, exclude_subspaces=True)
    if opts.packages:
        packages = {k: v for (k, v) in packages.iteritems() if v.name in opts.packages}

    # List up packages with its absolute path
    packages_by_name = {p.name: os.path.join(context.source_space_abs, path) for path, p in packages.iteritems()}

    doc_output = {}
    print('\nGenerating documents in {0}\n'.format(context.doc_space_abs))
    for name, path in packages_by_name.items():
        print(' - {0}'.format(name))
        output = generate_doc(name, path, context.doc_space_abs)
        doc_output[name] = output

    generates_index_page(context.doc_space_abs, packages_by_name.keys())

    print('\nDocument generation result. 0 may mean error. But it is fine most of time\n')
    for name, err in doc_output.items():
        print(" - {0} : {1}".format(name, str(err)))
    return 0

##############################################################################
# Helpers
##############################################################################

DOC_PROGRAM = 'rosdoc_lite'


def generate_doc(name, pkg_path, doc_path):
    document_path = doc_path + '/' + name
    args = [DOC_PROGRAM, '-o', document_path, pkg_path]
    output = subprocess.call(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output


def output(fd, html):
    for h in html:
        os.write(fd, h)
        os.write(fd, '\n')


def generates_index_page(doc_path, pkg_names):

    index_page = doc_path + '/index.html'
    fd = os.open(index_page, os.O_RDWR | os.O_CREAT)

    output(fd, templates.html_header)

    for pkg in pkg_names:
        link_html = '  <p><a href="' + pkg + '/html/index.html">' + pkg + '</a></p>'
        output(fd, [link_html])

    output(fd, templates.html_footer)
    os.close(fd)
