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
import multiprocessing

import subprocess
import traceback

try:
    from queue import Queue # Python3
except ImportError:
    from Queue import Queue # Python2

import catkin_pkg.packages as catkin_packages
import ckx_tools.argument_parsing as argument_parsing
import ckx_tools.common as common
import ckx_tools.execution.job_server as job_server
import ckx_tools.metadata as metadata

from ckx_tools.context import Context
from ckx_tools.execution.executor import execute_jobs
from ckx_tools.execution.executor import run_until_complete
from ckx_tools.execution.jobs import Job
from ckx_tools.execution.stages import CommandStage
from ckx_tools.execution.controllers import ConsoleStatusController
from ckx_tools.terminal_color import ColorMapper
from ckx_tools.utils import which

from . import templates

color_mapper = ColorMapper()
clr = color_mapper.clr

##############################################################################
# Entry Point API
##############################################################################

def help_string():
    instructions = clr("@!Examples@|\n\n  \
  @{cf}ckx rosdoc@| : @{yf}doc all packages in the source workspace@|\n  \
  @{cf}ckx rosdoc ecl_build ecl_time_lite@| : @{yf}doc only the listed packages@|\n\n  \
")
    return instructions

def prepare_arguments(parser):
    parser.epilog = help_string()
    argument_parsing.add_context_args(parser) # workspace / profile args
    add = parser.add_argument
    add('packages', nargs='*', help="workspace packages to doc, if none are given, then all are generated")
    add('--verbose', '-v', action='store_true', default=False, help='Print output from doc generators in their full glory.')
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

    # Initialize job server
    job_server.initialize(
        max_jobs=None,  # let the job server decide
        max_load=None,
        gnu_make_enabled=False)

    # List of packages, curtail if restricted list is specified
    packages = catkin_packages.find_packages(context.source_space_abs, exclude_subspaces=True)
    if opts.packages:
        packages = {k: v for (k, v) in packages.iteritems() if v.name in opts.packages}

    # List up packages with its absolute path
    packages_by_name = {p.name: os.path.join(context.source_space_abs, path) for path, p in packages.iteritems()}

    # doc_output = {}
    stages = []
    print('\nGenerating documents in {0}\n'.format(context.doc_space_abs))
    for name, path in packages_by_name.items():
        print(' - {0}'.format(name))
        stages.append(generate_doc_stage(name, path, context.doc_space_abs, context.workspace))
        # output = generate_doc(name, path, context.doc_space_abs)
        # doc_output[name] = output
    job = Job(
        jid="rosdoc",  # unique job identifier
        deps=[],
        env_loader=load_env,  # get_env_loader(package, context),
        stages=stages)
    event_queue = Queue()
    status_thread = ConsoleStatusController(
        'rosdoc',
        job_labels=['rosdoc', 'lite'],
        jobs=[job],
        max_toplevel_jobs=multiprocessing.cpu_count(),
        available_jobs=[],  # [pkg.name for _, pkg in context.packages],
        whitelisted_jobs= [],
        blacklisted_jobs=[],
        event_queue=event_queue,
        show_buffered_stdout=opts.verbose,
    )
    status_thread.start()
    # Block while running N jobs asynchronously
    try:
        unused_all_succeeded = run_until_complete(execute_jobs(
            'rosdoc',
            jobs=[job],
            locks={},
            event_queue=event_queue,
            log_path=context.log_space_abs,
            max_toplevel_jobs=multiprocessing.cpu_count()
            ))
    except Exception:
        status_thread.keep_running = False
        status_thread.join(1.0)
        common.wide_log(str(traceback.format_exc()))
    status_thread.join(1.0)

    generates_index_page(context.doc_space_abs, packages_by_name.keys())

#     print('\nDocument generation result. 0 may mean error. But it is fine most of time\n')
#     for name, err in doc_output.items():
#         print(" - {0} : {1}".format(name, str(err)))
#     print("")
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

def generate_doc_stage(name, pkg_path, doc_path, workspace_path):
    document_path = doc_path + '/' + name
    cmd = [DOC_PROGRAM, '-o', document_path, pkg_path]
    return CommandStage(
        label=name,
        cmd=cmd,
        cwd=workspace_path,
        occupy_job=True
        )


def output(fd, html):
    for h in html:
        os.write(fd, h)
        os.write(fd, '\n')


def generates_index_page(doc_path, pkg_names):

    index_page = doc_path + '/index.html'
    fd = os.open(index_page, os.O_RDWR | os.O_CREAT)

    output(fd, templates.html_header)

    for pkg in pkg_names:
        link_html = '  <a href="' + pkg + '/html/index.html">' + pkg + '</a><br/>'
        output(fd, [link_html])

    output(fd, templates.html_footer)
    os.close(fd)

def load_env(base_env):
    """
    @todo need a better environment than this so it can actually find
    rosdoc_lite without having to pre-load the environment from outside.

    :param base_env: usually this is just os.environ as is
    """
    return base_env


