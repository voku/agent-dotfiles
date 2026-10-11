#!/bin/sh
# Offline private-prefix setup; never modifies startup files or installs tools.
case "${1-}" in
    -h|--help|'')
        printf '%s\n' 'Usage: ./install.sh [install|verify|uninstall] --prefix ABSOLUTE_PATH [--revision FULL_COMMIT_SHA]' 'Install requires an independently approved full commit SHA and a clean checkout.' 'Default operation: install. Python 3.10+ and Git are required; no downloads occur.'
        exit 0 ;;
    install|verify|uninstall) operation=$1; shift ;;
    *) operation=install ;;
esac
# Validate prefix here: the lower-level API also supports resolved local paths.
expect_prefix=false
for argument do
    if [ "$expect_prefix" = true ]; then
        case "$argument" in /*) ;; *) printf '%s\n' 'agent-dotfiles: prefix must be absolute' >&2; exit 2 ;; esac
        expect_prefix=false
    fi
    case "$argument" in
        --prefix) expect_prefix=true ;;
        --prefix=*) case "${argument#--prefix=}" in /*) ;; *) printf '%s\n' 'agent-dotfiles: prefix must be absolute' >&2; exit 2 ;; esac ;;
        --source|--source=*) printf '%s\n' 'agent-dotfiles: install.sh always uses its own checkout; --source is unsupported' >&2; exit 2 ;;
    esac
done
case "$0" in */*) script_parent=${0%/*}; [ -n "$script_parent" ] || script_parent=/ ;; *) script_parent=. ;; esac
script_root=$(CDPATH='' cd -P -- "$script_parent" && printf '%s/' "$PWD") || exit 2
script_root=${script_root%/}
if ! command -v python3 >/dev/null 2>&1; then
    printf '%s\n' 'agent-dotfiles: python3 is required (Python 3.10+)' >&2
    exit 2
fi
if [ "$operation" = install ]; then
    exec python3 "$script_root/tools/install.py" install --source "$script_root" "$@"
fi
exec python3 "$script_root/tools/install.py" "$operation" "$@"
