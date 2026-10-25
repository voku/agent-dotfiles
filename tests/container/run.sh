#!/usr/bin/env bash
# Run ShellCheck and the Bashunit suite in a throwaway Debian container.
# Usage: tests/container/run.sh [bashunit args...]   (default: tests/shell --strict)
# The repository is mounted read-only and copied inside; nothing on the host changes.
set -eu

here="$(cd "$(dirname "$0")" && pwd -P)"
root="$(cd "$here/../.." && pwd -P)"
command -v docker >/dev/null || { echo "run.sh: docker is required" >&2; exit 1; }

build_args=()
if [ -n "${CODEX_PROXY_CERT:-}" ]; then
  [ -f "$CODEX_PROXY_CERT" ] || { echo "run.sh: CODEX_PROXY_CERT is not a file" >&2; exit 1; }
  build_args+=(--secret "id=proxy_ca,src=$CODEX_PROXY_CERT")
fi
docker build "${build_args[@]}" -q -t agent-dotfiles-check "$here" >/dev/null
[ "$#" -gt 0 ] || set -- tests/shell --strict
docker run --rm -v "$root":/src:ro agent-dotfiles-check bash -c '
  cd /src &&
  shellcheck --severity=warning -s bash .bashrc .shellrc .functions .exports .redpill/lib/*.sh tests/container/run.sh &&
  echo "shellcheck: ok" &&
  cp -R /src /tmp/work && cd /tmp/work && bashunit "$@"' bash "$@"
