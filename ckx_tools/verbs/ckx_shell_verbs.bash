# Catkin Shell Verbs

function __ckx_help_augmented() {
  # Print out an augmented --help line

  # Get ckx executable
  CKX=$1

  # Add our shell verbs to the main helpline
  ORIGINAL_HELP_TEXT="$($CKX --help)"
  AUGMENTED_HELP_TEXT=""

  # Read each line of the help text, preserving whitespace
  while IFS= read -r LINE; do
    if [[ $LINE =~ "^\s+clean\s+" ]]; then
      # Insert cd summary
      AUGMENTED_HELP_TEXT+="$CKX_CD_SUMMARY\n$LINE\n"
    elif [[ $LINE =~ "^\s+profile\s+" ]]; then
      # Insert source summary
      AUGMENTED_HELP_TEXT+="$LINE\n$CKX_SOURCE_SUMMARY\n"
    elif [[ $LINE =~ "^ckx command" ]]; then
      # Update summary
      AUGMENTED_HELP_TEXT+="ckx command with shell verbs\n"
    elif [[ $LINE =~ "^\s+\[\s*[a-z]+\s*\|{0,1}" ]]; then
      # Update verb list
      VERB_LIST=${LINE/build/build | cd}
      VERB_LIST=${VERB_LIST/profile/source | profile}
      VERB_LIST="$(echo "$VERB_LIST" | fmt -c -w 80)"
      AUGMENTED_HELP_TEXT+="$VERB_LIST\n"
    else
      # Pass-though
      AUGMENTED_HELP_TEXT+="$LINE\n"
    fi
  done <<< "$ORIGINAL_HELP_TEXT"
  echo $AUGMENTED_HELP_TEXT
}

function ckx() {
  # Define help lines
  CKX_CD_SUMMARY='    cd   	Changes directory to a package or space.'
  CKX_SOURCE_SUMMARY='    source      Sources a resultspace environment.'

  # Get actual ckx executable
  # Using `command` we ignore shell functions
  CKX="$(command which ckx)"

  # Get setup file extension
  if [ -n "$ZSH_VERSION" ]; then
    SHELL_EXT="zsh"
  elif [ -n "$BASH_VERSION" ]; then
    SHELL_EXT="bash"
  else
    SHELL_EXT=""
  fi

  # Capture original args
  if [[ "$SHELL_EXT" == "bash" ]]; then
      ORIG_ARGS=$@
  else
      ORIG_ARGS=(${@[*]})
  fi

  # Handle main arguments
  OPTSPEC=":hw-:"
  WORKSPACE_ARGS=""

  # Process main arguments
  while getopts "$OPTSPEC" optchar ; do
    case "${optchar}" in
      -)
        case "${OPTARG}" in
          # TODO: replace --args below with `$1` ?
          workspace) WORKSPACE_ARGS="--workspace $2"; OPTIND=$(( $OPTIND + 1 ));;
          profile) PROFILE_ARGS="--profile $2"; OPTIND=$(( $OPTIND + 1 ));;
          help) __ckx_help_augmented $CKX; return;;
        esac;;
      w) WORKSPACE_ARGS="--workspace $2";;
      h) __ckx_help_augmented $CKX; return;;
      *);;
    esac
  done

  # Pass the arguments through xargs to remove extra spaces
  # that can be in the result in some shells, e.g. zsh.
  # See: https://github.com/ckx/ckx_tools/pull/417
  MAIN_ARGS=$(echo "${WORKSPACE_ARGS} ${PROFILE_ARGS}" | xargs)

  # Get subcommand
  SUBCOMMAND="$1"

  # Check if there's no subcommand
  if [ -z "$SUBCOMMAND" ]; then
    __ckx_help_augmented $CKX; return
  fi

  # Shift subcommand
  shift

  # Handle shell verbs
  case "${SUBCOMMAND}" in
    cd) cd "$($CKX locate $MAIN_ARGS $@)";;
    source) source "$($CKX locate $MAIN_ARGS -d)/setup.$SHELL_EXT";;
    *) $CKX ${ORIG_ARGS}
  esac
}
