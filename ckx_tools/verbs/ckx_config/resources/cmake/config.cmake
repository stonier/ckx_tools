
###############################################################################
# Build Configuration
###############################################################################

###########################
# Parameterised Variables
###########################
set(CKX_DOC_PREFIX "%(config_doc_prefix)s" CACHE PATH "Document root location")
set(CKX_WORKSPACE "%(config_workspace)s" CACHE PATH "Location of the associated workspace")

###########################
# CMake
###########################

set(CMAKE_VERBOSE_MAKEFILE FALSE CACHE BOOL "Verbosity in the makefile compilations.")
# CMake's default build type is RelWithDebInfo, others include [Debug, Release, MinSizeRel]
set(CMAKE_BUILD_TYPE %(config_build_type)s CACHE STRING "Build mode type.")

# You can define neither CMAKE_CXX_FLAGS or CMAKE_CXX_FLAGS_INIT in the cache. They just
# get emptied by the cmake platform and compiler modules. We workaround this by dumping
# another variable in the cache and using that in a compiler overrides module.
set(CKX_CXX_FLAGS_INIT "${PLATFORM_CXX_FLAGS}" CACHE STRING "Initial flags that get passed to CMAKE_CXX_FLAGS via the cmake override file.")
set(CMAKE_USER_MAKE_RULES_OVERRIDE "%(config_override_file)s" CACHE PATH "User override file for setting global compiler flags.")

###########################
# Boost
###########################
# some useful boost variables should you wish to do some debugging of boost in
# cmake subprojects that call find package on boost
set(Boost_DEBUG FALSE CACHE BOOL "Debug boost.")
set(Boost_DETAILED_FAILURE_MSG FALSE CACHE BOOL "Detailed failure reports from boost.")

###########################
# Catkin
###########################
#
# The following cmake variables are controlled externally and overriden by
# catkin build commands. Do not set them here.
#
#  - CMAKE_INSTALL_PREFIX
#  - CATKIN_DEVEL_PREFIX

# The cmake prefix path, however will supplement whatever the catkin build command specifies.
# By and large, the usual method though will be to configure your underlay path list from outside.
# Example with a combination devel/install space. Start with the highest level workspace.
#
# set(CMAKE_PREFIX_PATH "/home/snorri/foo_ws/devel;/opt/ros/kinetic" CACHE PATH "semi-colon separated software/ros workspace paths.")
