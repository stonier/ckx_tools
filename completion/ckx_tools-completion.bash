# Copyright 2015 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ZSH support
if [[ -n ${ZSH_VERSION-} ]]; then
  autoload -U +X bashcompinit && bashcompinit
fi

_ckx_last_option()
{
  # search backwards for the last given option
  for (( i=${cword} ; i > 0 ; i-- )) ; do
    if [[ ${words[i]} == -* ]]; then
      echo ${words[i]}
      return
    fi
  done
}

_ckx_verb()
{
# search forwards to find ckx verb (neglecting global ckx opts)
  for (( i=1 ; i < ${cword} ; i++ )) ; do
    if [[ ${words[i]} == -* ]] ; then continue; fi
    if [[ ${ckx_verbs} == *${words[i]}* ]] ; then
      echo ${words[i]}
      return
    fi
  done
}

_ckx_pkgs()
{
  # return list of all packages
  ckx --no-color list --unformatted --quiet 2> /dev/null
}

# TODO:
# - parse --workspace and --profile options in order to complete outside of cwd

_ckx()
{
  local cur prev words cword ckx_verbs ckx_opts
  _init_completion || return # this handles default completion (variables, redirection)

  # complete to the following verbs
  local ckx_verbs="build clean config create init list profile"

  # filter for long options (from bash_completion)
  local OPTS_FILTER='s/.*\(--[-A-Za-z0-9]\{1,\}=\{0,1\}\).*/\1/p'

  # complete to verbs ifany of these are the previous word
  local ckx_opts=$(ckx --help 2>&1 | sed -ne $OPTS_FILTER | sort -u)

  # complete ckx profile subcommands
  local ckx_profile_args="add list remove rename set"

  local verb=$(_ckx_verb)
  case ${verb} in
    "")
      if [[ ${cur} == -* ]]; then
        COMPREPLY=($(compgen -W "${ckx_opts}" -- ${cur}))
      else
        COMPREPLY=($(compgen -W "${ckx_verbs}" -- ${cur}))
      fi
      ;;
    build)
      if [[ ${cur} == -* ]]; then
        local ckx_build_opts=$(ckx build --help 2>&1 | sed -ne $OPTS_FILTER | sort -u)
        COMPREPLY=($(compgen -W "${ckx_build_opts}" -- ${cur}))
      else
        COMPREPLY=($(compgen -W "$(_ckx_pkgs)" -- ${cur}))
      fi
      ;;
    config)
      # list all options
      local ckx_config_opts=$(ckx config --help 2>&1 | sed -ne $OPTS_FILTER | sort -u)
      COMPREPLY=($(compgen -W "${ckx_config_opts}" -- ${cur}))

      # list package names when --whitelist or --blacklist was given as last option
      if [[ ${cur} != -* && $(_ckx_last_option) == --*list ]] ; then
        COMPREPLY+=($(compgen -W "$(_ckx_pkgs)" -- ${cur}))
      fi

      # list directory names when useful
      if [[ ${prev} == --extend || ${prev} == --*-space ]] ; then
        # add directory completion
        compopt -o nospace 2>/dev/null
        COMPREPLY+=($(compgen -d -S "/" -- ${cur}))
      fi
      ;;
    clean)
      local ckx_clean_opts=$(ckx clean --help 2>&1 | sed -ne $OPTS_FILTER | sort -u)
      COMPREPLY=($(compgen -W "${ckx_clean_opts}" -- ${cur}))
      ;;
    create)
      if [[ "${words[@]}" == *" pkg"* ]] ; then
        local ckx_create_pkg_opts=$(ckx create pkg --help 2>&1 | sed -ne $OPTS_FILTER | sort -u)
        COMPREPLY=($(compgen -W "${ckx_create_pkg_opts}" -- ${cur}))
      else
        COMPREPLY=($(compgen -W "pkg" -- ${cur}))
      fi
      ;;
    profile)
      case ${prev} in
        profile)
          COMPREPLY=($(compgen -W "${ckx_profile_args}" -- ${cur}))
          ;;
        set|rename|remove)
          COMPREPLY=($(compgen -W "$(ckx --no-color profile list --unformatted)" -- ${cur}))
          ;;
        *)
          COMPREPLY=()
          ;;
      esac
      ;;
    init)
      local ckx_init_opts=$(ckx init --help 2>&1 | sed -ne $OPTS_FILTER | sort -u)
      COMPREPLY=($(compgen -W "${ckx_init_opts}" -- ${cur}))
      ;;
    list)
      local ckx_list_opts=$(ckx list --help 2>&1 | sed -ne $OPTS_FILTER | sort -u)
      COMPREPLY=($(compgen -W "${ckx_list_opts}" -- ${cur}))
      ;;
  esac

  return 0
}

complete -F _ckx ckx
