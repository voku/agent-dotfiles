#!/bin/sh
# Plan only. Runtime activation never installs developer tools.
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
exec python3 "$script_dir/tools/bootstrap_plan.py" "$@"
