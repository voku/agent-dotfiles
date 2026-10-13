#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/bin" "$tmp/home/.local/opt"
prefix="$tmp/home/.local/opt/agent-dotfiles"
revision=0000000000000000000000000000000000000000

cat >"$tmp/bin/apt-get" <<'APT'
#!/bin/sh
printf '%s\n' "$*" >>"$BOOTSTRAP_APT_LOG"
exit 0
APT
chmod +x "$tmp/bin/apt-get"
cat >"$tmp/bin/id" <<'ID'
#!/bin/sh
if [ "${1-}" = -u ]; then printf '%s\n' 0; else exec /usr/bin/id "$@"; fi
ID
chmod +x "$tmp/bin/id"
export BOOTSTRAP_APT_LOG="$tmp/apt.log"

# With a working planner, default bootstrap emits JSON and never calls apt or
# creates the requested prefix.
PATH="$tmp/bin:$PATH" "$repo_root/bootstrap.sh" --prefix "$prefix" --revision "$revision" >"$tmp/plan.out"
[[ -s "$tmp/plan.out" ]]
[[ ! -e "$BOOTSTRAP_APT_LOG" && ! -e "$prefix" ]]
grep -q 'Read-only bootstrap plan' "$tmp/plan.out"

# Invalid destinations are refused before even planning setup work.
for invalid_prefix in "$repo_root/.bootstrap-test-prefix" "$tmp/missing-parent/prefix"; do
    if PATH="$tmp/bin:$PATH" "$repo_root/bootstrap.sh" --prefix "$invalid_prefix" --revision "$revision" >"$tmp/invalid.out" 2>&1; then
        printf '%s\n' "expected invalid prefix to be refused: $invalid_prefix" >&2
        exit 1
    fi
done
[[ ! -e "$BOOTSTRAP_APT_LOG" ]]

# Simulate a bare system without a usable Python. Planning remains read-only.
cat >"$tmp/bin/python3" <<'PYTHON'
#!/bin/sh
exit 1
PYTHON
chmod +x "$tmp/bin/python3"
PATH="$tmp/bin:$PATH" "$repo_root/bootstrap.sh" --prefix "$prefix" --revision "$revision" >"$tmp/no-python.out"
grep -q 'Python 3.10+ is missing' "$tmp/no-python.out"
[[ ! -e "$BOOTSTRAP_APT_LOG" && ! -e "$prefix" ]]

# Even with --apply, the missing-Python stage is limited to apt metadata and
# Python 3. It stops before applying the rest of the plan or creating a prefix.
if PATH="$tmp/bin:$PATH" "$repo_root/bootstrap.sh" --prefix "$prefix" --revision "$revision" --apply >"$tmp/apply.out" 2>&1; then
    printf '%s\n' 'expected the simulated Python prerequisite to remain unavailable' >&2
    exit 1
fi
grep -q '^update$' "$BOOTSTRAP_APT_LOG"
grep -q '^install -y -- python3$' "$BOOTSTRAP_APT_LOG"
[[ $(wc -l <"$BOOTSTRAP_APT_LOG") -eq 2 ]]
[[ ! -e "$prefix" ]]

printf '%s\n' 'bootstrap_test.sh: passed'
