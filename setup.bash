#!/bin/bash

# Script for setting up the development environment.

if [ "${VIRTUAL_ENV}" == "" ]; then
  workon ckx_tools
  if [ $? -ne 0 ]; then
    mkvirtualenv ckx_tools
    # probably some python setup.py target which will do this for you
    pip install catkin_pkg
    pip install pyyaml
    pip install wstool
  fi
fi
# Always pulling for now
echo "Pulling external roles"
python setup.py develop

echo ""
echo "Leave the virutal environment with 'deactivate'"
echo ""
echo "I'm grooty, you should be too."
echo ""
