#!/usr/bin/env bash
# Run ShellCheck and the Bashunit suite in a throwaway Debian container.
# Usage: tests/container/run.sh [bashunit args...]   (default: tests/shell --strict)
# The repository is mounted read-only and copied inside; nothing on the host changes.
set -eu

here="$(cd "$(dirname "$0")" && pwd -P)"
root="$(cd "$here/../.." && pwd -P)"
version=0.50.1
cache="${XDG_CACHE_HOME:-$HOME/.cache}/agent-dotfiles"
bashunit="$cache/bashunit-$version"

command -v docker >/dev/null || { echo "run.sh: docker is required" >&2; exit 1; }
if [ ! -x "$bashunit" ]; then
  mkdir -p "$cache"
  curl -fsSL "https://github.com/TypedDevs/bashunit/releases/download/$version/bashunit" -o "$bashunit.part"
  chmod +x "$bashunit.part" && mv "$bashunit.part" "$bashunit"
fi

docker build -q -t agent-dotfiles-check "$here" >/dev/null
[ "$#" -gt 0 ] || set -- tests/shell --strict
docker run --rm -v "$root":/src:ro -v "$bashunit":/usr/local/bin/bashunit:ro agent-dotfiles-check bash -c '
  cd /src &&
  shellcheck --severity=warning -s bash .bashrc .shellrc .functions .exports .redpill/lib/*.sh tests/container/run.sh &&
  echo "shellcheck: ok" &&
  cp -R /src /tmp/work && cd /tmp/work && bashunit "$@"' bash "$@"
