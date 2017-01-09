
###############################################################################
# Build Configuration
###############################################################################

###########################
# Parameterised Variables
###########################
set(CKX_UNDERLAYS "%(config_underlays)s" CACHE PATH "Semi-colon separated list of underlay roots.")
set(CKX_DOC_PREFIX "%(config_doc_prefix)s" CACHE PATH "Document root location")

###########################
# CMake
###########################

set(CMAKE_VERBOSE_MAKEFILE FALSE CACHE BOOL "Verbosity in the makefile compilations.")
# CMake's default buidl type is RelWithDebInfo, others include [Debug, Release, MinSizeRel]
set(CMAKE_BUILD_TYPE %(config_build_type)s CACHE STRING "Build mode type.")
set(CMAKE_PREFIX_PATH "${CKX_UNDERLAYS}" CACHE PATH "semi-colon separated software/ros workspace paths.")

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
# Note that the following variables are controlled externally and overriden by
# catkin build commands. Do not set them here.
#
#  - CMAKE_INSTALL_PREFIX
#  - CATKIN_DEVEL_PREFIX
#  - CATKIN_BLACKLIST_PACKAGES "List of ';' separated packages to exclude"
#  - CATKIN_WHITELIST_PACKAGES "List of ';' separated packages to build (must be a complete list)"
