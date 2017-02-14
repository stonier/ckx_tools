import argparse
from distutils import log
import os
import site
from stat import ST_MODE
import sys

from setuptools import find_packages
from setuptools import setup
from setuptools.command.install import install

# Setup installation dependencies, removing some so they
# can build on the ppa
install_requires = [
    'catkin-pkg > 0.2.9',
    'setuptools',
    'PyYAML',
    'osrf-pycommon > 0.1.1',
    'rospkg',
    'vci',
    'vcstool'
]
if sys.version_info[0] == 2 and sys.version_info[1] <= 6:
    install_requires.append('argparse')

# Figure out the resources that need to be installed
this_dir = os.path.abspath(os.path.dirname(__file__))
osx_resources_path = os.path.join(
    this_dir,
    'ckx_tools',
    'notifications',
    'resources',
    'osx',
    'catkin build.app')
osx_notification_resources = [os.path.join(dp, f)
                              for dp, dn, fn in os.walk(osx_resources_path)
                              for f in fn]
src_path = os.path.join(this_dir, 'ckx_tools')
osx_notification_resources = [os.path.relpath(x, src_path)
                              for x in osx_notification_resources]


def _resolve_prefix(prefix, type):
    osx_system_prefix = '/System/Library/Frameworks/Python.framework/Versions'
    if type == 'man':
        if prefix == '/usr':
            return '/usr/share'
        if sys.prefix.startswith(osx_system_prefix):
            return '/usr/share'
    elif type == 'bash_comp':
        if prefix == '/usr':
            return '/'
        if sys.prefix.startswith(osx_system_prefix):
            return '/'
    elif type == 'zsh_comp':
        if sys.prefix.startswith(osx_system_prefix):
            return '/usr/local'
    else:
        raise ValueError('not supported type')
    return prefix


def get_data_files(prefix):
    data_files = []

    # Bash completion
    bash_comp_dest = os.path.join(_resolve_prefix(prefix, 'bash_comp'),
                                  'etc/bash_completion.d')
    data_files.append((bash_comp_dest,
                       ['completion/ckx_tools-completion.bash']))

    # Zsh completion
    zsh_comp_dest = os.path.join(_resolve_prefix(prefix, 'zsh_comp'),
                                 'share/zsh/site-functions')
    data_files.append((zsh_comp_dest, ['completion/_ckx']))
    return data_files


class PermissiveInstall(install):

    def run(self):
        install.run(self)
        if os.name == 'posix':
            for file in self.get_outputs():
                # all installed files should be readable for anybody
                mode = ((os.stat(file)[ST_MODE]) | 0o444) & 0o7777
                log.info("changing permissions of %s to %o" % (file, mode))
                os.chmod(file, mode)

        # Provide information about bash completion after default install.
        if (sys.platform.startswith("linux") and
                self.install_data == "/usr/local"):
            log.info("""
----------------------------------------------------------------
To enable tab completion, add the following to your '~/.bashrc':

  source {0}

----------------------------------------------------------------
""".format(os.path.join(self.install_data,
                        'etc/bash_completion.d',
                        'ckx_tools-completion.bash')))

parser = argparse.ArgumentParser(add_help=False)
prefix_group = parser.add_mutually_exclusive_group()
prefix_group.add_argument('--user', '--home', action='store_true')
prefix_group.add_argument('--prefix', default=None)

opts, _ = parser.parse_known_args(sys.argv)
userbase = site.getuserbase() if opts.user else None
prefix = userbase or opts.prefix or sys.prefix

setup(
    name='ckx_tools',
    version='0.5.14',
    packages=find_packages(exclude=['tests*', 'docs*']),  # ['ckx_tools'],  # find_packages(exclude=['tests', 'docs']), <-- broken, it picks up sub-packages, e.g. tests.unit
    package_data={
        'ckx_tools': [
            'notifications/resources/linux/*',
            'verbs/ckx_config/resources/cmake/*',
            'verbs/ckx_config/resources/templates/*',
            'verbs/ckx_config/resources/toolchains/buildroot/*',
            'verbs/ckx_config/resources/toolchains/ubuntu/*',
            'verbs/ckx_config/resources/toolchains/code_sourcery/*',
            'verbs/ckx_config/resources/toolchains/nexell/*',
            'verbs/ckx_config/resources/platforms/default.cmake',
            'verbs/ckx_config/resources/platforms/generic/*',
            'verbs/ckx_config/resources/platforms/arm/*',
            'verbs/ckx_config/resources/platforms/intel/*',
            'verbs/ckx_shell_verbs.bash',
            'docs/examples',
        ] + osx_notification_resources
    },
    data_files=get_data_files(prefix),
    install_requires=install_requires,
    author='Daniel Stonier',
    author_email='d.stonier@gmail.com',
    maintainer='Daniel Stonier',
    maintainer_email='d.stonier@gmail.com',
    url='http://ckx-tools.readthedocs.org/',
    keywords=['catkin'],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
    description="'X' tools for working with catkin.",
    long_description="Provides command line tools for working with catkin.",
    license='Apache 2.0',
    # test_suite='tests',
    entry_points={
        'console_scripts': [
            'ckx = ckx_tools.commands.catkin:main',
        ],
        'ckx_tools.commands.catkin.verbs': [
            'build = ckx_tools.verbs.ckx_build:description',
            'clean = ckx_tools.verbs.ckx_clean:description',
            'config = ckx_tools.verbs.ckx_config:description',
            'create = ckx_tools.verbs.ckx_create:description',
            'env = ckx_tools.verbs.ckx_env:description',
            'list = ckx_tools.verbs.ckx_list:description',
            'locate = ckx_tools.verbs.ckx_locate:description',
            'profile = ckx_tools.verbs.ckx_profile:description',
            'rosdep = ckx_tools.verbs.ckx_rosdep:description',
            'rosdoc = ckx_tools.verbs.ckx_rosdoc:description',
            'ws = ckx_tools.verbs.ckx_ws:description',
        ],
        'ckx_tools.jobs': [
            'catkin = ckx_tools.jobs.catkin:description',
            'cmake = ckx_tools.jobs.cmake:description',
        ],
    },
    cmdclass={'install': PermissiveInstall},
)
