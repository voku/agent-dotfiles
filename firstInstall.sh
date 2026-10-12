#!/bin/sh
# Plan only. Runtime activation never installs developer tools.
set -eu
if ! command -v python3 >/dev/null 2>&1; then
  printf "%s\n" "Python 3.10+ is required to run the tool planner; install it using an approved package manager and retry." >&2
  exit 2
fi
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
  printf "%s\n" "Python 3.10+ is required to run the tool planner; the detected Python is too old or cannot start." >&2
  exit 2
fi
case "$0" in
    */*) script_parent=${0%/*}; [ -n "$script_parent" ] || script_parent=/ ;;
    *) script_parent=. ;;
esac
script_dir=$(CDPATH='' cd -P -- "$script_parent" && printf '%s' "$PWD")
exec python3 "$script_dir/tools/bootstrap_plan.py" "$@"
