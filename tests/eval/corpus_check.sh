#!/usr/bin/env bash
# Mechanical correctness check of the helpers on real repositories.
#
# This is NOT the agent evaluation in issue #12: it measures whether helper
# output equals clean native output on real code, in Bash and Zsh. It says
# nothing about model tokens, speed or productivity.
#
# Usage: tests/eval/corpus_check.sh [-n MAX_REPOS] [-s bash,zsh] DIR_OR_REPO...
#   DIR_OR_REPO  a Git repository, or a directory whose children are repositories
# Exit 0 only if every check passed. Reads repositories; writes only to a temp dir.
set -u

here="$(cd "$(dirname "$0")" && pwd -P)"
root="$(cd "$here/../.." && pwd -P)"
max=12
shells=bash,zsh
while getopts n:s: opt; do
  case $opt in n) max=$OPTARG ;; s) shells=$OPTARG ;; *) exit 64 ;; esac
done
shift $((OPTIND - 1))
[ "$#" -gt 0 ] || { echo "usage: corpus_check.sh [-n MAX] [-s bash,zsh] DIR_OR_REPO..." >&2; exit 64; }

repos=()
for arg in "$@"; do
  if [ -e "$arg/.git" ]; then repos+=("$arg")
  else for child in "$arg"/*/; do [ -e "${child}.git" ] && [ -f "${child}composer.json" ] && repos+=("${child%/}"); done
  fi
done
[ "${#repos[@]}" -gt 0 ] || { echo "corpus_check: no repositories found" >&2; exit 66; }
repos=("${repos[@]:0:$max}")

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
pass=0; fail=0
for sh in ${shells//,/ }; do
  command -v "$sh" >/dev/null || { echo "corpus_check: $sh not installed, skipped"; continue; }
  profile=.bashrc; flags="--noprofile --norc"
  [ "$sh" = zsh ] && { profile=.zshrc; flags="-f"; }
  for repo in "${repos[@]}"; do
    name="$(basename "$repo")"
    start=$SECONDS
    # shellcheck disable=SC2086
    out="$(EVAL_TMP="$tmp" timeout "${CORPUS_TIMEOUT:-900}" env -u BASH_ENV "$sh" $flags -c '. "$1" || exit 71; . "$2" "$3"' x \
        "$root/$profile" "$here/repo_checks.sh" "$(cd "$repo" && pwd -P)" 2>&1 </dev/null)"; rc=$?
    [ "$rc" -eq 0 ] || out="${out}"$'\n'"FAIL"$'\t'"runner"$'\t'"exit status $rc"
    while IFS=$'\t' read -r verdict check detail; do
      [ -n "$verdict" ] || continue
      printf '%s\t%s\t%s\t%s\t%s\n' "$sh" "$name" "$verdict" "$check" "$detail"
      if [ "$verdict" = PASS ]; then pass=$((pass + 1)); else fail=$((fail + 1)); fi
    done <<< "$out"
    printf '# %s %s took %ss\n' "$sh" "$name" "$((SECONDS - start))" >&2
  done
done
printf 'corpus_check: %s passed, %s failed (%s repositories, shells: %s)\n' "$pass" "$fail" "${#repos[@]}" "$shells"
[ "$fail" -eq 0 ]
