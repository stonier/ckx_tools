#!/bin/bash

# Helpful if you are calling from something like a desktop
# launcher that does not have an environment set yet.
# Doesn't harm if you are already in a shell session
if [ -f /etc/bashrc ]; then
  . /etc/bashrc
fi
if [ -f ~/.profile ]; then
  . ~/.profile
fi

# Grab the built environment if it already exists. We
# always assume it is in ./devel. This could be otherwise
# but we have had no use case requiring it yet.
PWD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -f ${PWD}/devel/setup.bash ]; then
  source ${PWD}/devel/setup.bash
  alias cddevel="cd ${PWD}/devel"
fi

# CKX_BUILD_ROOT is usually inserted into devel/setup.bash, but
# in case it was built with other than `ckx build`, then we
# also set it here. It is used by 'ckx build' to automagically
# work from anywhere if you are already in a workspace session
if [ -z "${CKX_BUILD_ROOT+xxx}" ]; then
  export CKX_BUILD_ROOT=${PWD}
fi

# CKX_WORKSPACE is used by 'ckx ws' to automagically work from
# anywhere if you are already in a workspace session
export CKX_WORKSPACE=%(cwd)s

cd ${CKX_WORKSPACE}

###########################
# Colours
###########################

export BOLD="\e[1m"
export CYAN="\e[36m"
export GREEN="\e[32m"
export YELLOW="\e[33m"
export RED="\e[31m"
export RESET="\e[0m"

echo ""
echo -e "${CYAN}CKX_BUILD_ROOT: ${YELLOW}${CKX_BUILD_ROOT}${RESET}"
echo -e "${CYAN}CKX_WORKSPACE : ${YELLOW}${CKX_WORKSPACE}${RESET}"
echo ""
echo "I'm grooty, you should be too."
echo ""