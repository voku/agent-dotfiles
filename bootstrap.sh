#!/bin/sh
# Explicit Debian/Ubuntu setup: install the reviewed checkout into a private prefix,
# then verify its manifest and emit a session-only Git configuration loader.
set -eu

usage() {
    printf '%s\n' 'Usage: ./bootstrap.sh --prefix ABSOLUTE_PATH --revision FULL_COMMIT_SHA [--profile minimal|debug|php] [--apply]' \
      'Default: print a read-only package and runtime installation plan.' \
      '--apply: install the reviewed allowlisted packages and private-prefix runtime.' \
      'Applying package changes requires Debian/Ubuntu, apt-get and root or noninteractive sudo.'
}

prefix=
revision=
profile=minimal
apply=no
while [ "$#" -gt 0 ]; do
    case "$1" in
        --prefix) [ "$#" -ge 2 ] || { usage >&2; exit 2; }; prefix=$2; shift 2 ;;
        --revision) [ "$#" -ge 2 ] || { usage >&2; exit 2; }; revision=$2; shift 2 ;;
        --profile) [ "$#" -ge 2 ] || { usage >&2; exit 2; }; profile=$2; shift 2 ;;
        --apply) apply=yes; shift ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'bootstrap: unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
done
case "$prefix" in /*) ;; *) printf '%s\n' 'bootstrap: --prefix must be absolute' >&2; exit 2 ;; esac
case "$prefix" in */) printf '%s\n' 'bootstrap: --prefix must not end with a slash' >&2; exit 2 ;; esac
case "/$prefix/" in */../*) printf '%s\n' 'bootstrap: --prefix must not contain path traversal' >&2; exit 2 ;; esac
case "$revision" in *[!0-9a-f]*|'') printf '%s\n' 'bootstrap: --revision must be a full lowercase commit SHA' >&2; exit 2 ;; esac
[ "${#revision}" -eq 40 ] || { printf '%s\n' 'bootstrap: --revision must be a full commit SHA' >&2; exit 2; }
case "$profile" in minimal|debug|php) ;; *) printf '%s\n' 'bootstrap: unsupported profile' >&2; exit 2 ;; esac

case "$0" in */*) root=${0%/*}; [ -n "$root" ] || root=/ ;; *) root=. ;; esac
root=$(CDPATH='' cd -P -- "$root" && pwd)
prefix_parent=${prefix%/*}
[ -n "$prefix_parent" ] || prefix_parent=/
[ -d "$prefix_parent" ] || { printf '%s\n' 'bootstrap: --prefix parent must already exist' >&2; exit 2; }
_agent_prefix_probe=$prefix
while [ "$_agent_prefix_probe" != / ]; do
    [ ! -L "$_agent_prefix_probe" ] || { printf '%s\n' 'bootstrap: --prefix cannot contain symlink paths' >&2; exit 2; }
    _agent_prefix_probe=${_agent_prefix_probe%/*}
    [ -n "$_agent_prefix_probe" ] || _agent_prefix_probe=/
done
unset _agent_prefix_probe
if [ -e "$prefix" ]; then
    [ -d "$prefix" ] || { printf '%s\n' 'bootstrap: existing --prefix must be an empty directory' >&2; exit 2; }
    [ -z "$(find "$prefix" -mindepth 1 -print -quit)" ] \
        || { printf '%s\n' 'bootstrap: existing --prefix must be empty' >&2; exit 2; }
fi
prefix_canonical_parent=$(CDPATH='' cd -P -- "$prefix_parent" && pwd)
prefix_name=${prefix##*/}
if [ "$prefix_canonical_parent" = / ]; then
    prefix_canonical=/$prefix_name
else
    prefix_canonical=$prefix_canonical_parent/$prefix_name
fi
case "$prefix_canonical/" in "$root/"*) printf '%s\n' 'bootstrap: --prefix cannot be inside the source checkout' >&2; exit 2 ;; esac
case "$root/" in "$prefix_canonical/"*) printf '%s\n' 'bootstrap: --prefix cannot contain the source checkout' >&2; exit 2 ;; esac
has_python=no
python_bootstrapped=no
if command -v python3 >/dev/null 2>&1 \
    && python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' >/dev/null 2>&1; then
    has_python=yes
fi

if [ "$apply" = yes ] && [ "$has_python" = no ]; then
    # A bare supported Debian/Ubuntu host needs Python before the planner can
    # produce its complete package plan. This prerequisite is still behind the
    # same explicit --apply boundary as every later package change.
    distribution=$(sed -n 's/^ID=//p' /etc/os-release 2>/dev/null | sed 's/^"//; s/"$//')
    case "$distribution" in
        debian|ubuntu) ;;
        *) printf '%s\n' 'bootstrap: missing Python can only be bootstrapped on Debian/Ubuntu' >&2; exit 2 ;;
    esac
    command -v apt-get >/dev/null 2>&1 || { printf '%s\n' 'bootstrap: apt-get is required (Debian/Ubuntu only)' >&2; exit 2; }
    if [ "$(id -u)" -ne 0 ] && ! command -v sudo >/dev/null 2>&1; then
        printf '%s\n' 'bootstrap: --apply needs root or noninteractive sudo to install Python 3 first' >&2
        exit 2
    fi
    if [ "$(id -u)" -eq 0 ]; then
        apt-get update
        DEBIAN_FRONTEND=noninteractive apt-get install -y -- python3
    elif command -v sudo >/dev/null 2>&1; then
        sudo -n apt-get update || { printf '%s\n' 'bootstrap: run as root or establish noninteractive sudo access first' >&2; exit 2; }
        sudo -n env DEBIAN_FRONTEND=noninteractive apt-get install -y -- python3 || { printf '%s\n' 'bootstrap: Python prerequisite installation failed' >&2; exit 2; }
    else
        printf '%s\n' 'bootstrap: --apply needs root or noninteractive sudo to install Python 3 first' >&2
        exit 2
    fi
    command -v python3 >/dev/null 2>&1 \
        && python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' >/dev/null 2>&1 \
        || { printf '%s\n' 'bootstrap: Python 3.10+ is required after installing the prerequisite' >&2; exit 2; }
    has_python=yes
    python_bootstrapped=yes
fi

if [ "$apply" = yes ]; then
    distribution=$(sed -n 's/^ID=//p' /etc/os-release 2>/dev/null | sed 's/^"//; s/"$//')
    case "$distribution" in
        debian|ubuntu) ;;
        *) printf '%s\n' 'bootstrap: setup application is supported only on Debian/Ubuntu' >&2; exit 2 ;;
    esac
fi

if [ "$has_python" = yes ]; then
    plan=$("$root/firstInstall.sh" plan --profile "$profile")
    packages=$(printf '%s' "$plan" | python3 -c 'import json,sys; x=json.load(sys.stdin); assert x["manager"] in (None, "apt"), "supported distribution must use apt"; print("\n".join(x["package_command_argv"][3:]) if x["package_command_argv"] else "")')
else
    packages='python3 (required before package planning)'
    plan='Python 3.10+ is missing; on a fresh Debian/Ubuntu host, --apply installs this prerequisite first.'
fi

printf '%s\n' 'Read-only bootstrap plan:' "$plan"
if [ "$apply" != yes ]; then
    printf '%s\n' 'No package or prefix changes were made. Review the plan, then rerun with --apply to install.'
    exit 0
fi

if [ "$has_python" != yes ]; then
    printf '%s\n' 'bootstrap: Python planning prerequisite is unavailable' >&2
    exit 2
fi

if [ "$python_bootstrapped" = yes ]; then
    printf '%s\n' 'Python 3.10+ is ready. No diagnostics, other packages, or prefix files were changed.' \
      'Review the complete plan above, then rerun with --apply to install the planned packages and private-prefix runtime.'
    exit 0
fi

if [ -n "$packages" ]; then
    distribution=$(sed -n 's/^ID=//p' /etc/os-release 2>/dev/null | sed 's/^"//; s/"$//')
    case "$distribution" in
        debian|ubuntu) ;;
        *) printf '%s\n' 'bootstrap: package installation is supported only on Debian/Ubuntu' >&2; exit 2 ;;
    esac
    command -v apt-get >/dev/null 2>&1 || { printf '%s\n' 'bootstrap: apt-get is required (Debian/Ubuntu only)' >&2; exit 2; }
    if [ "$(id -u)" -ne 0 ] && ! command -v sudo >/dev/null 2>&1; then
        printf '%s\n' 'bootstrap: run as root or install the approved packages with an administrator' >&2
        exit 2
    fi
    if [ "$(id -u)" -eq 0 ]; then
        apt-get update
        # Every package name comes from the fixed reviewed planner allowlist.
        # shellcheck disable=SC2086
        DEBIAN_FRONTEND=noninteractive apt-get install -y -- $packages
    else
        sudo -n apt-get update || { printf '%s\n' 'bootstrap: run as root or establish noninteractive sudo access first' >&2; exit 2; }
        # shellcheck disable=SC2086
        sudo -n env DEBIAN_FRONTEND=noninteractive apt-get install -y -- $packages || { printf '%s\n' 'bootstrap: package installation failed' >&2; exit 2; }
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
