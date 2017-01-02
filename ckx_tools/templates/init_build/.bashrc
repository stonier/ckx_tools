#!/bin/bash
if [ -f /etc/bashrc ]; then
  . /etc/bashrc
fi
if [ -f ~/.profile ]; then
  . ~/.profile
fi
export CKX_WORKSPACE=%(cwd)s
if [ -d ${CKX_WORKSPACE}/devel ]; then
  source ${CKX_WORKSPACE}/devel/setup.bash
  alias cddevel="cd ${CKX_WORKSPACE}/devel"
  alias m1="export ROS_MASTER_URI=http://localhost:11311"
  alias m2="export ROS_MASTER_URI=http://localhost:11312"
  alias m3="export ROS_MASTER_URI=http://localhost:11313"
  alias m4="export ROS_MASTER_URI=http://localhost:11314"
  alias m5="export ROS_MASTER_URI=http://localhost:11315"
fi

