#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/home"
mkdir -p "$tmp/diff-repo"
cat >"$tmp/home/.gitconfig" <<'GITCONFIG'
[user]
	name = original-user
GITCONFIG
before_global=$(sha256sum "$tmp/home/.gitconfig")

# Nested shell source is single-quoted to preserve runtime expansion and printf
# escapes; these warnings inspect the enclosing literal, not the child script.
# shellcheck disable=SC1012,SC1078
env -i PATH="$PATH" HOME="$tmp/home" GIT_CONFIG_GLOBAL="$tmp/home/.gitconfig" \
    GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=user.name GIT_CONFIG_VALUE_0=inherited \
    GIT_CONFIG_KEY_1=user.email GIT_CONFIG_VALUE_1=inherited@example.test \
    bash --noprofile --norc -c '
set -eu
root=$1
diff_repo=$2
. "$root/activate.sh"
[[ "$GIT_CONFIG_COUNT" == 7 ]]
[[ "$(git config --get core.pager)" == cat ]]
[[ "$(git config --get user.name)" == inherited ]]
. "$root/activate.sh"
[[ "$GIT_CONFIG_COUNT" == 7 ]]
. "$root/git-env.sh"
[[ "$GIT_CONFIG_COUNT" == 7 ]]

# The Git helper preserves complete staged/unstaged binary patch bytes and
# native argument-error status/stderr.
git -C "$diff_repo" init -q
printf 'before\n' >"$diff_repo/text.txt"
printf '\000\001\002' >"$diff_repo/binary.bin"
git -C "$diff_repo" add text.txt binary.bin
git -C "$diff_repo" commit -qm fixture
printf 'after\n' >"$diff_repo/text.txt"
git -C "$diff_repo" add text.txt
printf '\003\004\005' >"$diff_repo/binary.bin"
(cd "$diff_repo" && agent_diff --cached --binary) >"$diff_repo/helper-staged.diff"
(cd "$diff_repo" && git --no-pager -c color.ui=false diff --no-ext-diff --no-textconv --cached --binary) >"$diff_repo/native-staged.diff"
cmp "$diff_repo/helper-staged.diff" "$diff_repo/native-staged.diff"
(cd "$diff_repo" && agent_diff --binary) >"$diff_repo/helper-unstaged.diff"
(cd "$diff_repo" && git --no-pager -c color.ui=false diff --no-ext-diff --no-textconv --binary) >"$diff_repo/native-unstaged.diff"
cmp "$diff_repo/helper-unstaged.diff" "$diff_repo/native-unstaged.diff"
if (cd "$diff_repo" && agent_diff --definitely-invalid) >"$diff_repo/helper.out" 2>"$diff_repo/helper.err"; then helper_status=0; else helper_status=$?; fi
if (cd "$diff_repo" && git --no-pager -c color.ui=false diff --no-ext-diff --no-textconv --definitely-invalid) >"$diff_repo/native.out" 2>"$diff_repo/native.err"; then native_status=0; else native_status=$?; fi
[[ "$helper_status" == "$native_status" ]]
cmp "$diff_repo/helper.out" "$diff_repo/native.out"
cmp "$diff_repo/helper.err" "$diff_repo/native.err"

# Detect and preserve an environment entry appended by another consumer.
GIT_CONFIG_KEY_7=alias.safe=status
GIT_CONFIG_VALUE_7="status --short"
export GIT_CONFIG_KEY_7 GIT_CONFIG_VALUE_7
GIT_CONFIG_COUNT=8
export GIT_CONFIG_COUNT
if agent_deactivate 2>/dev/null; then
    printf "%s\n" "deactivation should preserve the appended consumer entry" >&2
    exit 1
fi
[[ "$GIT_CONFIG_COUNT" == 8 && "$GIT_CONFIG_KEY_7" == alias.safe=status ]]
[[ "$(typeset -f agent_context >/dev/null; echo $?)" == 0 ]]

unset GIT_CONFIG_KEY_7 GIT_CONFIG_VALUE_7
GIT_CONFIG_COUNT=7
export GIT_CONFIG_COUNT
agent_deactivate
[[ "$GIT_CONFIG_COUNT" == 2 ]]
[[ "$GIT_CONFIG_KEY_0" == user.name && "$GIT_CONFIG_VALUE_0" == inherited ]]
[[ "$GIT_CONFIG_KEY_1" == user.email && "$GIT_CONFIG_VALUE_1" == inherited@example.test ]]
[[ "$(git config --get user.name)" == inherited ]]
[[ -z "${AGENT_DOTFILES_SESSION_ACTIVE-}" ]]
! typeset -f agent_context >/dev/null 2>&1
. "$root/activate.sh"
[[ "$GIT_CONFIG_COUNT" == 7 ]]
agent_deactivate
[[ "$GIT_CONFIG_COUNT" == 2 ]]
' bash-test "$repo_root" "$tmp/diff-repo"

after_global=$(sha256sum "$tmp/home/.gitconfig")
[[ "$before_global" == "$after_global" ]]

# A bad inherited count must fail activation without leaking shell helpers or Git slots.
env -i PATH="$PATH" HOME="$tmp/home" GIT_CONFIG_COUNT=invalid \
    bash --noprofile --norc -c '
set -eu
root=$1
if . "$root/activate.sh" 2>/dev/null; then
    printf "%s\n" "activation should reject an invalid inherited Git count" >&2
    exit 1
fi
[[ "$GIT_CONFIG_COUNT" == invalid ]]
[[ -z "${AGENT_DOTFILES_HOME-}" && -z "${AGENT_DOTFILES_SESSION_ACTIVE-}" ]]
! typeset -f agent_context >/dev/null 2>&1
! typeset -f agent_git_deactivate >/dev/null 2>&1
' bash-test "$repo_root"

if command -v zsh >/dev/null 2>&1; then
    env -i PATH="$PATH" HOME="$tmp/home" zsh -f -c '
set -eu
. "$1/activate.sh"
[[ "$GIT_CONFIG_COUNT" == 5 ]]
. "$1/activate.sh"
[[ "$GIT_CONFIG_COUNT" == 5 ]]
agent_deactivate
[[ -z "${GIT_CONFIG_COUNT-}" ]]
[[ -z "${AGENT_DOTFILES_SESSION_ACTIVE-}" ]]
' zsh-test "$repo_root"
fi

printf '%s\n' 'environment_test.sh: passed'
