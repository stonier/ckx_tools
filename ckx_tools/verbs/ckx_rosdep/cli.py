#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/stonier/ckx_tools/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Implementation of the 'ckx rosdep' verb.
"""

##############################################################################
# Imports
##############################################################################

import os
import subprocess
import sys
import traceback

try:
    from queue import Queue  # Python3
except ImportError:
    from Queue import Queue  # Python2

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
    default_track = common.get_default_track()

    parser.epilog = help_string()
    argument_parsing.add_context_args(parser)  # workspace / profile args
    add = parser.add_argument

    add('--install', '-i', action='store_true', default=False,
        help='Install all rosdeps for this build profile (including underlays)')
    add('--keys', '-k', action='store_true', default=False,
        help='List all rosdep keys required by this build profile (including underlays)')
    add('--track', action='store', default=default_track, help='force the track (rosdistro) if the default guess is not accurate %s [%s]' % (common.VALID_TRACKS, default_track))
    return parser


def main(opts):
    # Are we in a parallel build profile? If so, prefer that over the active one
    if not opts.profile:
        enclosing_profile = metadata.find_enclosing_profile(os.getcwdu(), opts.workspace)
        if enclosing_profile:
            print(clr("@!\nInfo: in a parallel build folder, prefer this profile [%s]\n@|" % enclosing_profile))
            opts.profile = enclosing_profile

    # Load the context
    context = Context.load(opts.workspace, opts.profile, opts)

    # Initialize job server
    job_server.initialize(
        max_jobs=1,
        max_load=None,
        gnu_make_enabled=False)

    underlays = context.cmake_prefix_path.split(';')
    if opts.install:
        # alternative: the ckx tools job server way, but rosdep install needs sudo and this adds root logs!
        # create_and_execute_job('install', cmd, context.workspace, context.log_space_abs)
        # NOTE: don't use log here - user is probably running sudo, prefer sys.stdout.write
        sys.stdout.write(clr("@!Installing Rosdeps@|\n"))
        cmd = rosdeps_install_command(context, underlays, opts.track)
        try:
            proc = subprocess.Popen(
                cmd, cwd=context.source_space_abs, shell=False,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=os.environ.copy()
            )
        except OSError as e:
            sys.stdout.write(clr("@{rf}[ERROR] failed command '{0}': {1}").format(cmd, e))
            return 1
        error_flag = False
        while True:
            line = proc.stdout.readline().decode('utf8', 'replace')
            line = unicode(line)
            if proc.returncode is not None or not line:
                break
            if line.startswith("ERROR"):
                error_flag = True
            if error_flag:
                sys.stdout.write(clr("@{rf}" + line + "@!"))
            else:
                sys.stdout.write(line)
        proc.wait()
        # perhaps check proc.returncode and print ERROR if true
        return 0
    if opts.keys:
        sys.stdout.write(clr("@!List Rosdep Keys@|\n"))
        cmd = rosdeps_keys_command(context, underlays, opts.track)
        try:
            proc = subprocess.Popen(
                cmd, cwd=context.source_space_abs, shell=False,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=os.environ.copy()
            )
        except OSError as e:
            sys.stdout.write(clr("@{rf}[ERROR] failed command '{0}': {1}").format(cmd, e))
            return 1
        proc.wait()
        out, err = proc.communicate()
        if err:
            sys.stdout.write(clr("@{rf}" + err + "@!"))
        else:
            sys.stdout.write(clr("@{gf}  Keys@!\n"))
            rosdep_keys = [s for s in out.split("\n") if s]  # drop empty lines
            for key in sorted(rosdep_keys):
                sys.stdout.write(clr("   @{cf}+@{yf} {0}\n").format(key))

        # create_and_execute_job('keys', cmd, context.workspace, context.log_space_abs)
        return 0
    return 0

##############################################################################
# Helpers
##############################################################################


def extend_cmd_from_paths(underlays):
    extended_cmd = []
    sys.stdout.write(clr("  @{gf}From Paths@!\n"))
    for underlay in underlays:
        underlay_path = underlay
        # if it is a devel workspace -> hunt for the sources
        enclosing_workspace = metadata.find_enclosing_workspace(underlay_path)
        if enclosing_workspace:
            underlay_source_path = os.path.abspath(os.path.join(enclosing_workspace, "src"))
            if os.path.isdir(underlay_source_path):
                underlay_path = underlay_source_path
        if os.path.isdir(underlay_path):
            extended_cmd += ['--from-paths', underlay_path]
            sys.stdout.write(clr("   @{cf}+@{yf} {0}\n").format(underlay_path))
        else:
            sys.stdout.write(clr("   @{cf}-@{rf} {0} [not found]\n").format(underlay_path))
    return extended_cmd


def rosdeps_keys_command(context, underlays, rosdistro):
    """
    :param str underlays: comma separated string of underlays
    :returns: list of strings comprising the command to execute
    """
    source_path = os.path.abspath(os.path.join(context.workspace, "src"))
    cmd = [which('rosdep'), 'keys', '-r']
    cmd += extend_cmd_from_paths(underlays)
    cmd += ['--from-paths', source_path, '--ignore-src', '--rosdistro', rosdistro]
    return cmd


def rosdeps_install_command(context, underlays, rosdistro):
    """
    :param str underlays: comma separated string of underlays
    :returns: list of strings comprising the command to execute
    """
    source_path = os.path.abspath(os.path.join(context.workspace, "src"))

    cmd = [which('rosdep'), 'install']
    cmd += extend_cmd_from_paths(underlays)
    cmd += ['--from-paths', source_path, '--ignore-src', '--rosdistro', rosdistro, '-y']
    return cmd


def create_and_execute_job(job_name, cmd, workspace_path, log_path):
    """
    Put the rosdep job on the job server.
    :param str job_name: user friendly label for the job
    :param [str] cmd: actual command to execute
    """
    stages = []
    stages.append(CommandStage(
        job_name,
        cmd,
        cwd=workspace_path,
        occupy_job=True
    ))
    job = Job(
        jid="rosdep",  # unique job identifier
        deps=[],
        env_loader=load_env,  # get_env_loader(package, context),
        stages=stages)
    event_queue = Queue()
    status_thread = ConsoleStatusController(
        'rosdep',
        job_labels=['rosdep', 'install'],
        jobs=[job],
        max_toplevel_jobs=1,
        available_jobs=[],  # [pkg.name for _, pkg in context.packages],
        whitelisted_jobs=[],
        blacklisted_jobs=[],
        event_queue=event_queue,
        show_buffered_stdout=True,
    )
    status_thread.start()
    # Block while running N jobs asynchronously
    try:
        unused_all_succeeded = run_until_complete(execute_jobs(
            'rosdep',
            jobs=[job],
            locks={},
            event_queue=event_queue,
            log_path=log_path,
            max_toplevel_jobs=1
        ))
    except Exception:
        status_thread.keep_running = False
        status_thread.join(1.0)
        common.wide_log(str(traceback.format_exc()))
    status_thread.join(1.0)

    return 0


def load_env(base_env):
    """
    Don't need an extended environment for this job. Just
    return the base environment directly.

    :param base_env: usually this is just os.environ as is
    """
    return base_env

