#!/usr/bin/env bash
# bashunit contracts for explicit Bash/Zsh activation. Each case runs a fresh
# shell against a copy of the profile kept in a deliberately hostile path.

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
ASSETS=(.bashrc .zshrc .shellrc .exports .functions .redpill/lib/activation.sh .redpill/lib/deactivation.sh .redpill/config/agent.env .redpill/config/ripgreprc)

function set_up() {
  RUN_ENV=()
  # Physical path: activation resolves symlinks (macOS /var -> /private/var).
  TEST_ROOT="$(cd -P -- "$(mktemp -d)" && pwd -P)"
  HOME_COPY="$TEST_ROOT/agent tools [雪] \$literal"
  local asset
  for asset in "${ASSETS[@]}"; do
    mkdir -p -- "$HOME_COPY/$(dirname -- "$asset")"
    cp -- "$PROJECT_ROOT/$asset" "$HOME_COPY/$asset"
  done
  mkdir -p -- "$TEST_ROOT/user"
  for asset in .bashrc .bash_profile .zshrc .zprofile; do
    printf 'touch "%s/unsafe-startup"\n' "$TEST_ROOT" > "$TEST_ROOT/user/$asset"
  done
}

function tear_down() {
  rm -rf -- "$TEST_ROOT"
}

# Run SCRIPT in a fresh shell ($1 = profile path, remaining args follow).
# Sets STATUS, STDOUT and STDERR. Usage: run_shell bash|zsh SCRIPT [ARG...]
function run_shell() {
  local shell="$1" script="$2" profile
  shift 2
  if [ "$shell" = zsh ]; then profile=.zshrc; else profile=.bashrc; fi
  local -a flags=(--noprofile --norc)
  [ "$shell" = zsh ] && flags=(-f)
  STATUS=0
  STDOUT="$(env -i PATH="$PATH" HOME="$TEST_ROOT/user" ${RUN_ENV[@]+"${RUN_ENV[@]}"} \
      "$shell" "${flags[@]}" -c "$script" consumer "$HOME_COPY/$profile" "$@" 2>"$TEST_ROOT/stderr")" || STATUS=$?
  STDERR="$(cat -- "$TEST_ROOT/stderr")"
}

# Prints present/absent; avoids `case` inside $( ), which Bash 3.2 mis-parses.
function contains_word() {
  if [[ "$2" == *"$1"* ]]; then printf present; else printf absent; fi
}

function available_shells() {
  command -v bash >/dev/null && printf 'bash\n'
  command -v zsh >/dev/null && printf 'zsh\n'
  return 0
}

function test_activation_is_silent_and_preserves_shell_state() {
  local shell
  for shell in $(available_shells); do
    run_shell "$shell" '
set -eu
before_options=$-; before_path=$PATH; before_pwd=$PWD; before_args=$#
. "$1"
[ "$before_options" = "$-" ] && [ "$before_path" = "$PATH" ] && [ "$before_pwd" = "$PWD" ] && [ "$before_args" = "$#" ]
[ "$AGENT_DOTFILES_HOME" = "$2" ]' "$HOME_COPY"
    assert_same '0' "$STATUS"
    assert_same '' "$STDOUT"
    assert_same '' "$STDERR"
    assert_same 'absent' "$([ -e "$TEST_ROOT/unsafe-startup" ] && echo present || echo absent)"
  done
}

function test_agent_defaults_are_exported_and_environment_is_fully_restored() {
  local shell
  for shell in $(available_shells); do
    run_shell "$shell" '
before=$(command env | sort)
. "$1" || exit 10
[ "$PAGER" = cat ] && [ "$GIT_PAGER" = cat ] && [ "$NO_COLOR" = 1 ] || exit 11
[ "$GIT_TERMINAL_PROMPT" = 0 ] && [ "$COMPOSER_NO_INTERACTION" = 1 ] || exit 12
[ "$npm_config_progress" = false ] && [ "$PIP_NO_INPUT" = 1 ] && [ "$CARGO_TERM_COLOR" = never ] || exit 13
[ "$RIPGREP_CONFIG_PATH" = "$AGENT_DOTFILES_HOME/.redpill/config/ripgreprc" ] || exit 14
agent_deactivate
after=$(command env | sort)
[ "$before" = "$after" ] || { printf "%s\n" "$after" | diff - /dev/null | head; exit 15; }
[ "${AGENT_DOTFILES_EXPORTED+x}${AGENT_DOTFILES_FUNCTIONS+x}" = "" ] || exit 16
for fn in $(grep -o "^agent_[a-z_]*" "$2/.functions") agent_deactivate; do
  ! typeset -f "$fn" >/dev/null 2>&1 || exit 17
done' "$PROJECT_ROOT"
    assert_same '0' "$STATUS"
  done
}

function test_host_chosen_settings_survive_activation_and_deactivation() {
  local shell
  for shell in $(available_shells); do
    RUN_ENV=(PAGER=less NO_COLOR=0 npm_config_fund=true)
    run_shell "$shell" '. "$1" || exit 10; [ "$PAGER" = less ] && [ "$NO_COLOR" = 0 ] && [ "$npm_config_fund" = true ] || exit 11; agent_deactivate; [ "$PAGER" = less ] && [ "$NO_COLOR" = 0 ] && [ "$npm_config_fund" = true ]' x
    RUN_ENV=()
    assert_same '0' "$STATUS"
  done
}

function test_owned_name_collision_refuses_without_partial_state() {
  local shell definition
  for shell in $(available_shells); do
    for definition in 'agent_git() { :; }' 'agent_rg() { :; }' 'agent_diff() { :; }' \
        'agent_deactivate() { :; }' 'alias agent_git=true' 'AGENT_DOTFILES_HOME=existing'; do
      run_shell "$shell" "$definition; . \"\$1\"" x
      assert_same '2' "$STATUS"
      assert_contains 'agent-dotfiles:' "$STDERR"
    done
  done
  run_shell bash 'agent_rg() { :; }; . "$1" 2>/dev/null; [ "${AGENT_DOTFILES_HOME+x}" != x ] && [ "${PAGER+x}" != x ]' x
  assert_same '0' "$STATUS"
}

function test_missing_or_directory_assets_refuse_activation() {
  local shell asset
  for asset in .exports .functions .redpill/lib/deactivation.sh .redpill/config/agent.env .redpill/config/ripgreprc; do
    mv -- "$HOME_COPY/$asset" "$HOME_COPY/$asset.saved"
    for shell in $(available_shells); do
      run_shell "$shell" '. "$1"; rc=$?; [ "${AGENT_DOTFILES_HOME+x}" != x ] || exit 99; exit $rc' x
      assert_same '2' "$STATUS"
      assert_contains "$asset" "$STDERR"
    done
    mv -- "$HOME_COPY/$asset.saved" "$HOME_COPY/$asset"
  done
}

function test_agent_git_preserves_argv_and_exit_status() {
  local repo="$TEST_ROOT/repo [λ]" shell
  git init -q "$repo"
  printf 'x\n' > "$repo/-odd name.txt"
  for shell in $(available_shells); do
    run_shell "$shell" '. "$1" || exit 10; shift; agent_git -C "$1" status --porcelain=v1; rc=$?; agent_git -C "$1" rev-parse --verify absent 2>/dev/null; exit $((rc * 10 + $?))' "$repo"
    assert_same '128' "$STATUS"
    assert_contains 'odd name.txt' "$STDOUT"
  done
}

function test_agent_rg_ignores_host_configuration_and_reports_no_match() {
  local shell
  printf -- '--no-such-flag\n' > "$TEST_ROOT/rgrc"
  printf 'needle\n' > "$TEST_ROOT/haystack.txt"
  for shell in $(available_shells); do
    RUN_ENV=()
    run_shell "$shell" '. "$1" || exit 10; shift; RIPGREP_CONFIG_PATH="$2" agent_rg -n -F -- needle "$1"/haystack.txt >/dev/null || exit 11; agent_rg -F -- absent "$1"/haystack.txt; exit $?' "$TEST_ROOT" "$TEST_ROOT/rgrc"
    assert_same '1' "$STATUS"
  done
}

function test_agent_rg_is_native_ripgrep_and_inherits_its_binary_file_limitation() {
  local shell
  mkdir -p -- "$TEST_ROOT/tree"
  printf 'needle\n\0tail\n' > "$TEST_ROOT/tree/nul.php"
  printf 'xx\0needle\0yy\n' > "$TEST_ROOT/tree/real.bin"
  printf 'needle\n' > "$TEST_ROOT/tree/plain.php"
  for shell in $(available_shells); do
    # Evidence for #70, not a guarantee: native ripgrep silently skips NUL-containing files in a recursive walk.
    run_shell "$shell" '. "$1" || exit 10; shift; agent_rg -l -F -- needle "$1"/tree' "$TEST_ROOT"
    assert_same '0' "$STATUS"
    assert_contains 'plain.php' "$STDOUT"
    assert_not_contains 'nul.php' "$STDOUT"
    # Caller opt-in: lists the NUL-containing source file and the binary match.
    run_shell "$shell" '. "$1" || exit 10; shift; agent_rg --binary -l -F -- needle "$1"/tree' "$TEST_ROOT"
    assert_contains 'nul.php' "$STDOUT"
    assert_contains 'real.bin' "$STDOUT"
    # ...without emitting raw NUL bytes, and with a visible notice.
    run_shell "$shell" '. "$1" || exit 10; shift; agent_rg --binary -n -F -- needle "$1"/tree | { tr -cd "\\0" | wc -c; }' "$TEST_ROOT"
    assert_same '0' "$(printf '%s' "$STDOUT" | tr -d ' ')"
    run_shell "$shell" '. "$1" || exit 10; shift; agent_rg --binary -n -F -- needle "$1"/tree' "$TEST_ROOT"
    assert_contains 'binary file matches' "$STDOUT"
  done
}

function test_agent_env_values_with_equals_and_spaces_survive_intact() {
  local shell
  printf 'ODD_VALUE=a=b c\n# comment\n\nSECOND=2\n' >> "$HOME_COPY/.redpill/config/agent.env"
  for shell in $(available_shells); do
    run_shell "$shell" '. "$1" || exit 10; [ "$ODD_VALUE" = "a=b c" ] && [ "$SECOND" = 2 ] || exit 11; agent_deactivate; [ "${ODD_VALUE+x}" != x ] && [ "${SECOND+x}" != x ]' x
    assert_same '0' "$STATUS"
  done
}

function test_every_helper_in_functions_is_protected_from_collisions() {
  local fn shell
  for fn in $(grep -o '^agent_[a-z_]*' "$PROJECT_ROOT/.functions"); do
    for shell in $(available_shells); do
      run_shell "$shell" "$fn() { :; }; . \"\$1\"" x
      assert_same '2' "$STATUS"
      assert_contains "$fn" "$STDERR"
    done
  done
}

function test_agent_head_marks_truncation_and_validates_input() {
  local shell
  for shell in $(available_shells); do
    run_shell "$shell" '. "$1" || exit 10; printf "a\nb\nc\nd" | agent_head 2' x
    assert_same "a
b
agent_head: TRUNCATED, showed 2 of 4 lines" "$STDOUT"
    run_shell "$shell" '. "$1" || exit 10; printf "a\nb\n" | agent_head 2' x
    assert_same "a
b" "$STDOUT"
    run_shell "$shell" '. "$1" || exit 10; printf "a\n" | agent_head nope' x
    assert_same '64' "$STATUS"
  done
}

function test_agent_diff_matches_native_git_despite_hostile_gitconfig() {
  local shell repo="$TEST_ROOT/diff repo [λ]"
  git init -q "$repo"
  printf 'before\n' > "$repo/text.txt"
  git -C "$repo" add text.txt
  git -C "$repo" -c user.name=t -c user.email=t@example.test commit -qm fixture
  printf 'after \n' > "$repo/text.txt"
  GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null \
    git -C "$repo" --no-pager -c color.ui=false diff --no-ext-diff --no-textconv > "$TEST_ROOT/native.diff"
  printf '[color]\n\tui = always\n[diff]\n\texternal = /nonexistent/driver\n' > "$TEST_ROOT/hostile-gitconfig"
  for shell in $(available_shells); do
    RUN_ENV=(GIT_CONFIG_GLOBAL="$TEST_ROOT/hostile-gitconfig" GIT_CONFIG_SYSTEM=/dev/null)
    run_shell "$shell" '. "$1" || exit 10; cd "$2" && agent_diff' "$repo"
    RUN_ENV=()
    assert_same '0' "$STATUS"
    assert_same "$(cat "$TEST_ROOT/native.diff")" "$STDOUT"
  done
}

function test_second_activation_refuses_and_a_deactivated_shell_can_reactivate() {
  local shell
  for shell in $(available_shells); do
    run_shell "$shell" '
. "$1" || exit 10
home=$AGENT_DOTFILES_HOME
. "$1"; [ "$?" = 2 ] || exit 11
[ "$AGENT_DOTFILES_HOME" = "$home" ] && type agent_git >/dev/null 2>&1 || exit 12
agent_deactivate
. "$1" || exit 13
agent_git --version >/dev/null || exit 14' "$HOME_COPY/$([ "$shell" = zsh ] && echo .zshrc || echo .bashrc)"
    assert_same '0' "$STATUS"
    assert_contains 'AGENT_DOTFILES_HOME already exists' "$STDERR"
  done
}

function test_child_shells_inherit_variables_but_not_functions() {
  local shell
  for shell in $(available_shells); do
    run_shell "$shell" '
. "$1" || exit 10
[ "$("$2" -c "printf %s \"\$PAGER\"")" = cat ] || exit 11
"$2" -c "command -v agent_git >/dev/null 2>&1" && exit 12
exit 0' "$shell"
    assert_same '0' "$STATUS"
  done
}

function test_activation_works_from_a_relative_path_with_newline_and_leading_dash() {
  local shell odd="$TEST_ROOT/-odd
dir" asset
  for asset in "${ASSETS[@]}"; do
    mkdir -p -- "$odd/$(dirname -- "$asset")"
    cp -- "$PROJECT_ROOT/$asset" "$odd/$asset"
  done
  for shell in $(available_shells); do
    local -a flags=(--noprofile --norc); local profile=.bashrc
    [ "$shell" = zsh ] && { flags=(-f); profile=.zshrc; }
    STATUS=0
    STDOUT="$(cd -- "$odd" && env -i PATH="$PATH" HOME="$TEST_ROOT/user" "$shell" "${flags[@]}" -c \
      '. "./$1" || exit 10; [ "$AGENT_DOTFILES_HOME" = "$PWD" ] || exit 11; agent_deactivate' x "$profile" 2>&1)" || STATUS=$?
    assert_same '0' "$STATUS"
    assert_same '' "$STDOUT"
  done
}

function test_symlinked_profile_is_refused_cleanly() {
  local shell
  for shell in $(available_shells); do
    local profile=.bashrc; [ "$shell" = zsh ] && profile=.zshrc
    ln -sfn "$HOME_COPY/$profile" "$TEST_ROOT/link$profile"
    run_shell "$shell" '. "$2"; rc=$?; [ "$rc" = 2 ] || exit 10; [ "${AGENT_DOTFILES_HOME+x}" = x ] && exit 11; exit 0' "$TEST_ROOT/link$profile"
    assert_same '0' "$STATUS"
    assert_contains '.shellrc is missing or unreadable' "$STDERR"
  done
}

function test_bashrc_refuses_a_posix_shell_without_defining_anything() {
  # macOS /bin/sh is Bash in POSIX mode and legitimately activates; only test a real non-Bash sh.
  [ -z "$(env -i PATH="$PATH" sh -c 'printf %s "${BASH_VERSION-}"')" ] || return 0
  STATUS=0
  STDERR="$(env -i PATH="$PATH" HOME="$TEST_ROOT/user" sh -c '. "$1"; rc=$?; command -v agent_git >/dev/null && exit 11; exit "$rc"' x "$HOME_COPY/.bashrc" 2>&1 >/dev/null)" || STATUS=$?
  assert_same '2' "$STATUS"
  assert_contains '.bashrc requires Bash' "$STDERR"
}

