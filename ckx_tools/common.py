##############################################################################
# Imports
##############################################################################

import os.path
import sys
import multiprocessing
import subprocess
import ast

from . import console
from . import python_setup
from . import config_cache

##############################################################################
# Constants
##############################################################################

DEFAULT_TRACK = "kinetic"
VALID_TRACKS = ["groovy", "hydro", "indigo", "jade", "kinetic"]
DEFAULT_ROSINSTALL_DATABASE = 'https://raw.github.com/stonier/ckx_tools/devel/rosinstalls'

##############################################################################
# Methods
##############################################################################


def initialise_ckx_tools_home():
    """
    Check that the ckx tools home exists otherwise try to create it.
    """
    home_dir = ckx_tools_home()
    if not os.path.exists(home_dir):
        if os.path.isfile(home_dir):
            raise RuntimeError("the ckx tools home ({0}) exists but is a file.".format(home_dir))
        os.makedirs(home_dir)


def ckx_tools_home():
    """
    Get directory location of '.ckx_tools' directory.

    @return: path to use use for the settings directory
    @rtype: str
    """
    home_dir = os.path.join(os.path.expanduser('~'), '.ckx_tools')
    return home_dir


def set_default_track(track=DEFAULT_TRACK):
    if track not in VALID_TRACKS:
        raise RuntimeError("The track '%s' is not a valid track. Choose from %s\n" % (track, VALID_TRACKS))
    filename = os.path.join(ckx_tools_home(), "track")
    f = open(filename, 'w+')
    try:
        f.write(track.encode('utf-8'))
    finally:
        f.close()
    return track


def set_rosinstall_database_uri(rosinstall_database=DEFAULT_ROSINSTALL_DATABASE):
    '''
      Set a uri for your rosinstall database.
    '''
    # could actually check that it is a valid uri though.
    filename = os.path.join(ckx_tools_home(), "rosinstall_database")
    f = open(filename, 'w+')
    try:
        f.write(rosinstall_database.encode('utf-8'))
    finally:
        f.close()
    return rosinstall_database


def get_default_track():
    filename = os.path.join(ckx_tools_home(), "track")
    try:
        f = open(filename, 'r')
    except IOError:
        set_default_track()
        return DEFAULT_TRACK
    track = f.read()
    f.close()
    return track


def get_rosinstall_database_uri():
    filename = os.path.join(ckx_tools_home(), "rosinstall_database")
    try:
        f = open(filename, 'r')
    except IOError:
        return set_rosinstall_database_uri()
    rosinstall_database = f.read()
    f.close()
    return rosinstall_database


def which(program):
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, unused_fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def is_same_dir(dir_a, dir_b):
    rel_path = os.path.relpath(os.path.abspath(dir_a), os.path.abspath(dir_b))
    if rel_path == ".":
        return True
    else:
        return False


def is_tty(stream):
    """Returns True if the given stream is a tty, else False"""
    return hasattr(stream, 'isatty') and stream.isatty()


def good_number_of_jobs():
    if 'ROS_PARALLEL_JOBS' in os.environ:
        jobs = os.environ['ROS_PARALLEL_JOBS']
    else:
        try:
            jobs = multiprocessing.cpu_count()
        except NotImplementedError:
            jobs = 1
    return jobs


def override_filename():
    return os.path.join(os.path.dirname(__file__), 'cmake', 'overrides.cmake')


def parent_directory(path):
    return os.path.abspath(os.path.join(path, os.pardir))


def create_symlink(src, dst, quiet=False):
    """
    Creates a symlink at dst to src.
    """
    if not os.path.exists(src):
        raise RuntimeError("'%s' is not a valid path" % src)
    try:
        os.symlink(src, dst)
        if not quiet:
            console.pretty_print('Creating symlink', console.white)
            console.pretty_print(' "%s" ' % dst, console.bold)
            console.pretty_print("->", console.white)
            console.pretty_println(' "%s." ' % src, console.bold)
    except Exception as ex_symlink:
        raise RuntimeError("Could not symlink '%s' to %s [%s]." % (src, dst, str(ex_symlink)))


def is_broken_symlink(link_path):
    '''
      Checks to see if the provided link_path is firstly, a link, and secondly if
      that link is broken.
    '''
    if os.path.islink(link_path):
        target_path = os.readlink(link_path)
        # Resolve relative symlinks
        if not os.path.isabs(target_path):
            target_path = os.path.join(os.path.dirname(link_path), target_path)
        if not os.path.exists(target_path):
            return True
    return False


def find_catkin(base_path, underlays_list=None):
    '''
      Search the underlays looking for catkin's toplevel.cmake and python module.
    '''
    if underlays_list is None:
        underlays_list = config_cache.get_underlays_list_from_config_cmake(base_path)
    catkin_toplevel = None
    catkin_python_path = None
    catkin_cmake_path = None
    for underlay in underlays_list:
        if os.path.isfile(os.path.join(underlay, 'share', 'catkin', 'cmake', 'toplevel.cmake')):
            # it is in an underlay's install space
            catkin_cmake_path = os.path.join(underlay, 'share', 'catkin', 'cmake')
            catkin_toplevel = os.path.join(underlay, 'share', 'catkin', 'cmake', 'toplevel.cmake')
            if os.path.isfile(os.path.join(underlay, python_setup.get_global_python_destination(), 'catkin', 'builder.py')):
                catkin_python_path = os.path.join(underlay, python_setup.get_global_python_destination())
            break
        elif os.path.isfile(os.path.join(underlay, python_setup.get_global_python_destination(), 'catkin', '__init__.py')):
            # it's probably a devel space
            console.error('Error: catkin seems to be buried in a chained devel space - not yet supporting this')
            # catkin_python_path = os.path.join(underlay, python_setup.get_global_python_destination())
            break
    return catkin_toplevel, catkin_python_path, catkin_cmake_path


def generate_underlay_environment(base_path):
    '''
      Parse all the underlay environment scripts to setup an initial environment for us to work in. This
      should be easier than manually crafting everything. We do maintain some more complexity than
      catkin_make though as we support a pyramid of underlays, not a linear chain.

      UNUSED and UNTESTED!
    '''
    underlays_list = config_cache.get_underlays_list_from_config_cmake(base_path)
    env = os.environ.copy()
    for underlay in reversed(underlays_list):
        print("\nUnderlay: %s" % underlay)
        env_script = os.path.join(underlay, 'env.sh')
        # Should validate that the script exists
        python_code = 'import os; print(dict(os.environ))'
        print [env_script, sys.executable, '-c', python_code]
        output = subprocess.check_output([env_script, sys.executable, '-c', python_code])
        print output
        # Not really positive what's going on here - this is what is in catkin.environment_cache.generate_environment_scripot
        # I think it just safely decodes strings in the dictionary.
        if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
            output = output.decode(sys.stdout.encoding)
        env_after = ast.literal_eval(output)
        # calculate added and modified environment variables
        modified = {}
        for key, value in env_after.items():
            if key not in env:
                env[key] = value
            elif env[key] != value:
                # Need to be careful here - we are dealing with paths that will need to be merged.
                modified[key] = [env[key], value]
        # Deal with modified keys
        for key in sorted(modified.keys()):
            (old_value, new_value) = modified[key]
            if(key.contains('PATH') or old_value.contains(os.pathsep) or new_value.contains(os.pathsep)):
                # Merge paths
                old_elements = os.pathsep.split(old_value)
                new_elements = os.pathsep.split(new_value)
                for element in new_elements:
                    if not old_elements.contains(element):
                        env[key] = env[key] + os.pathsep + element
            else:
                # it's a regular variable - take the latest value assigned to it (not we're sorting underlays in the correct (reverse) order of priority
                env[key] = new_value
    return env


def generate_pkg_config_path(base_path):
    '''
      Generate a list of pkg_config_paths from the underlays

      @param base_path : used to find the config.cmake which lists the underlays
      @return list of paths
    '''
    underlays_list = config_cache.get_underlays_list_from_config_cmake(base_path)
    pkg_config_path = []
    for underlay in underlays_list:
        if os.path.isdir(os.path.join(underlay, 'lib', 'pkgconfig')):
            pkg_config_path.append(os.path.join(underlay, 'lib', 'pkgconfig'))
    return pkg_config_path


def get_default_paths(isolated=False):
    suffix = "_isolated" if isolated else ""
    base_path = os.environ.get("CKX_BUILD_ROOT") or os.getcwd()  # Fallback if os.environ.get returns None
    build_path = os.path.join(base_path, 'build' + suffix)
    devel_path = os.path.join(base_path, 'devel' + suffix)
    source_path = os.path.join(base_path, 'src')
    return (base_path, build_path, devel_path, source_path)
