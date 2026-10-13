# Sourced inside an activated Bash or Zsh by corpus_check.sh; $1 is a Git repo.
# Prints one line per check: "PASS|FAIL<TAB>name<TAB>detail". POSIX-style so it
# runs unchanged in both shells. Read-only: every write goes to $EVAL_TMP.
repo=$1
cd "$repo" || exit 70
say() { printf '%s\t%s\t%s\n' "$1" "$2" "$3"; }
same() { if cmp -s "$2" "$3"; then say PASS "$1" "$4"; else say FAIL "$1" "differs: $4"; fi; }
HOSTILE_RG="$EVAL_TMP/hostile-rg.conf"
printf '%s\n' '--max-columns=20' '--glob=!*.php' '--color=always' '--max-count=1' > "$HOSTILE_RG"

# rg prints files in a different order on every run (parallel walk), so rg
# outputs are compared as sorted sets of lines.
# 1. agent_rg ignores a hostile host ripgrep config and equals a clean native run.
RIPGREP_CONFIG_PATH=/dev/null command rg --no-config --color=never -n 'function ' . > "$EVAL_TMP/rg.native" 2>&1; echo $? > "$EVAL_TMP/rg.native.rc"
RIPGREP_CONFIG_PATH="$HOSTILE_RG" agent_rg -n 'function ' . > "$EVAL_TMP/rg.agent" 2>&1; echo $? > "$EVAL_TMP/rg.agent.rc"
sort -o "$EVAL_TMP/rg.native" "$EVAL_TMP/rg.native"; sort -o "$EVAL_TMP/rg.agent" "$EVAL_TMP/rg.agent"
same rg-insulated "$EVAL_TMP/rg.native" "$EVAL_TMP/rg.agent" "$(wc -l < "$EVAL_TMP/rg.native" | tr -d ' ') match lines"
same rg-exit-status "$EVAL_TMP/rg.native.rc" "$EVAL_TMP/rg.agent.rc" "rc=$(cat "$EVAL_TMP/rg.native.rc")"

# 2. Activated plain `rg` loses no matches versus a clean native run (presentation only).
command rg --no-config --color=never -n 'function ' . > "$EVAL_TMP/rg.plain.native" 2>&1
command rg -n 'function ' . > "$EVAL_TMP/rg.plain.active" 2>&1
sort -o "$EVAL_TMP/rg.plain.native" "$EVAL_TMP/rg.plain.native"; sort -o "$EVAL_TMP/rg.plain.active" "$EVAL_TMP/rg.plain.active"
same rg-plain-no-hidden-matches "$EVAL_TMP/rg.plain.native" "$EVAL_TMP/rg.plain.active" "activated rg == native rg"

# 3. agent_diff equals clean native Git over the last commit, despite a hostile gitconfig.
if git rev-parse -q --verify HEAD~1 >/dev/null 2>&1; then
    printf '[color]\n\tui = always\n[diff]\n\texternal = /nonexistent/driver\n[core]\n\tpager = false\n' > "$EVAL_TMP/hostile-gitconfig"
    GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null command git --no-pager -c color.ui=false diff --no-ext-diff --no-textconv HEAD~1 HEAD > "$EVAL_TMP/diff.native" 2>&1
    GIT_CONFIG_GLOBAL="$EVAL_TMP/hostile-gitconfig" GIT_CONFIG_SYSTEM=/dev/null agent_diff HEAD~1 HEAD > "$EVAL_TMP/diff.agent" 2>&1
    same diff-insulated "$EVAL_TMP/diff.native" "$EVAL_TMP/diff.agent" "$(wc -c < "$EVAL_TMP/diff.native" | tr -d ' ') bytes"
else
    say PASS diff-insulated "single-commit repo, skipped"
fi
