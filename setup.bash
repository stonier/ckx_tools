#!/bin/bash

# Script for setting up the development environment.

if [ "${VIRTUAL_ENV}" == "" ]; then
  workon ckx_tools
  if [ $? -ne 0 ]; then
    mkvirtualenv ckx_tools
    if [ $? -ne 0 ]; then
    	sudo apt-get install virtualenvwrapper
    	mkvirtualenv ckx_tools
    fi
    # probably some python setup.py target which will do this for you
    pip install catkin_pkg
    pip install pyyaml
    pip install vcstool
    pip install vcs_extras
    pip install rospkg
  fi
fi
# Always pulling for now
python setup.py develop

echo ""
echo "Leave the virtual environment with 'deactivate'"
echo ""
echo "I'm grooty, you should be too."
echo ""

