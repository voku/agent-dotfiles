#!/usr/bin/env bash
# Explicit, offline entry point. Only the checkout containing this script is eligible.
set -euo pipefail
source_root="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
case "${1:-}" in
  install)
    shift
    exec python3 "$source_root/tools/install.py" install --source "$source_root" "$@"
    ;;
  verify|uninstall)
    operation="$1"
    shift
    exec python3 "$source_root/tools/install.py" "$operation" "$@"
    ;;
  *)
    printf '%s\n' 'Usage: ./install.sh install --revision FULL_COMMIT_SHA --prefix PRIVATE_PATH' \
      '       ./install.sh verify|uninstall --revision FULL_COMMIT_SHA --prefix PRIVATE_PATH' >&2
    exit 2
    ;;
esac
