#!/bin/sh
# Explicit Debian/Ubuntu setup: install the reviewed checkout into a private prefix,
# then verify its manifest and emit a session-only Git configuration loader.
set -eu

usage() {
    printf '%s\n' 'Usage: ./bootstrap.sh --prefix ABSOLUTE_PATH --revision FULL_COMMIT_SHA [--profile minimal|debug|php]' \
      'Installs missing allowlisted Debian/Ubuntu tools, installs this checkout, and verifies it.' \
      'Package installation requires apt-get and sufficient privileges.'
}

prefix=
revision=
profile=minimal
while [ "$#" -gt 0 ]; do
    case "$1" in
        --prefix) [ "$#" -ge 2 ] || { usage >&2; exit 2; }; prefix=$2; shift 2 ;;
        --revision) [ "$#" -ge 2 ] || { usage >&2; exit 2; }; revision=$2; shift 2 ;;
        --profile) [ "$#" -ge 2 ] || { usage >&2; exit 2; }; profile=$2; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'bootstrap: unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
done
case "$prefix" in /*) ;; *) printf '%s\n' 'bootstrap: --prefix must be absolute' >&2; exit 2 ;; esac
case "$revision" in *[!0-9a-f]*|'') printf '%s\n' 'bootstrap: --revision must be a full lowercase commit SHA' >&2; exit 2 ;; esac
[ "${#revision}" -eq 40 ] || { printf '%s\n' 'bootstrap: --revision must be a full commit SHA' >&2; exit 2; }
case "$profile" in minimal|debug|php) ;; *) printf '%s\n' 'bootstrap: unsupported profile' >&2; exit 2 ;; esac

case "$0" in */*) root=${0%/*}; [ -n "$root" ] || root=/ ;; *) root=. ;; esac
root=$(CDPATH='' cd -P -- "$root" && pwd)
command -v python3 >/dev/null 2>&1 || { printf '%s\n' 'bootstrap: Python 3.10+ is required before setup' >&2; exit 2; }
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' || { printf '%s\n' 'bootstrap: Python 3.10+ is required' >&2; exit 2; }
command -v apt-get >/dev/null 2>&1 || { printf '%s\n' 'bootstrap: apt-get is required (Debian/Ubuntu only)' >&2; exit 2; }

plan=$("$root/firstInstall.sh" plan --profile "$profile")
packages=$(printf '%s' "$plan" | python3 -c 'import json,sys; x=json.load(sys.stdin); assert x["manager"] == "apt", "supported distribution must use apt"; print("\n".join(x["package_command_argv"][3:]) if x["package_command_argv"] else "")')
if [ -n "$packages" ]; then
    if [ "$(id -u)" -eq 0 ]; then
        # Package names originate solely from the planner's fixed Debian allowlist.
        # shellcheck disable=SC2086
        apt-get update
        # shellcheck disable=SC2086
        DEBIAN_FRONTEND=noninteractive apt-get install -y -- $packages
    elif command -v sudo >/dev/null 2>&1; then
        # Never block an agent shell waiting for an interactive sudo password.
        sudo -n apt-get update || { printf '%s\n' 'bootstrap: run as root or establish noninteractive sudo access first' >&2; exit 2; }
        # shellcheck disable=SC2086
        sudo -n env DEBIAN_FRONTEND=noninteractive apt-get install -y -- $packages || { printf '%s\n' 'bootstrap: package installation failed' >&2; exit 2; }
    else
        printf '%s\n' 'bootstrap: run as root or install the missing packages with an approved administrator' >&2
        exit 2
    fi
fi

"$root/install.sh" --prefix "$prefix" --revision "$revision"
"$root/install.sh" verify --prefix "$prefix" --revision "$revision"

for tool in git rg jq curl; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        printf 'bootstrap: expected tool is still unavailable: %s\n' "$tool" >&2
        exit 1
    fi
done
if [ "$profile" = debug ]; then
    if ! command -v fd >/dev/null 2>&1 && ! command -v fdfind >/dev/null 2>&1; then
        printf '%s\n' 'bootstrap: expected fd or fdfind is still unavailable' >&2
        exit 1
    fi
    for tool in shellcheck hyperfine strace; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            printf 'bootstrap: expected tool is still unavailable: %s\n' "$tool" >&2
            exit 1
        fi
    done
fi

# Verify the session config through Git itself before reporting success.
. "$prefix/git-env.sh"
[ "$(git config --get core.pager)" = cat ] || { printf '%s\n' 'bootstrap: Git pager config verification failed' >&2; exit 1; }
[ "$(git config --get color.ui)" = false ] || { printf '%s\n' 'bootstrap: Git color config verification failed' >&2; exit 1; }
[ "$(git config --get diff.algorithm)" = histogram ] || { printf '%s\n' 'bootstrap: Git diff config verification failed' >&2; exit 1; }
[ "$(git config --get diff.renames)" = true ] || { printf '%s\n' 'bootstrap: Git rename config verification failed' >&2; exit 1; }
[ "$(git config --get log.date)" = iso-strict ] || { printf '%s\n' 'bootstrap: Git date config verification failed' >&2; exit 1; }

# GIT_CONFIG_COUNT augments Git configuration for shells that explicitly source
# this reviewed, manifest-verified file.
printf 'Setup verified. For a consistent Bash/Zsh task session, run: . %s/activate.sh\n' "$prefix"
