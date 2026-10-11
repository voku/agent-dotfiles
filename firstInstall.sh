#!/bin/sh
# Plan only. Runtime activation never installs developer tools.
set -eu
if ! command -v python3 >/dev/null 2>&1; then
  printf "%s\n" "Python 3.10+ is required to run the tool planner; install it using an approved package manager and retry." >&2
  exit 2
fi
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
exec python3 "$script_dir/tools/bootstrap_plan.py" "$@"
