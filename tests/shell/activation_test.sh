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
    for definition in 'agent_git() { :; }' 'agent_rg() { :; }' 'agent_history() { :; }' \
        'agent_blame() { :; }'  'agent_deactivate() { :; }' 'alias agent_git=true' 'AGENT_DOTFILES_HOME=existing'; do
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

function test_agent_require_reports_missing_old_and_satisfied_tools() {
  local shell
  for shell in $(available_shells); do
    run_shell "$shell" '. "$1" || exit 10; agent_require definitely-not-installed-tool; exit $?' x
    assert_same '1' "$STATUS"
    run_shell "$shell" '. "$1" || exit 10; agent_require git 999.0; exit $?' x
    assert_same '2' "$STATUS"
    run_shell "$shell" '. "$1" || exit 10; agent_require git 1.0 | cut -f1' x
    assert_same 'git' "$STDOUT"
    run_shell "$shell" '. "$1" || exit 10; agent_require; exit $?' x
    assert_same '64' "$STATUS"
  done
}

function test_agent_os_reports_key_value_facts() {
  local shell
  for shell in $(available_shells); do
    run_shell "$shell" '. "$1" || exit 10; agent_os' x
    assert_same '0' "$STATUS"
    assert_contains 'kernel=' "$STDOUT"
    assert_contains 'arch=' "$STDOUT"
  done
}

function test_agent_free_port_skips_a_listening_port() {
  command -v ss >/dev/null || command -v netstat >/dev/null || return 0
  local shell port
  python3 -c 'import socket,time
s=socket.socket(); s.bind(("127.0.0.1",0)); s.listen()
print(s.getsockname()[1], flush=True); time.sleep(20)' > "$TEST_ROOT/port" &
  local listener=$!
  while [ ! -s "$TEST_ROOT/port" ]; do sleep 0.05; done
  port="$(cat "$TEST_ROOT/port")"
  for shell in $(available_shells); do
    run_shell "$shell" '. "$1" || exit 10; agent_ports | grep -qx "$2" || exit 11; free=$(agent_free_port "$2") || exit 12; [ "$free" != "$2" ] && [ "$free" -gt "$2" ]' "$port"
    assert_same '0' "$STATUS"
  done
  kill "$listener" 2>/dev/null
}

function test_agent_json_formats_and_rejects_invalid_input() {
  local shell
  for shell in $(available_shells); do
    run_shell "$shell" '. "$1" || exit 10; printf "{\"a\":[1,2]}" | agent_json | tr -d " \n"' x
    assert_same '{"a":[1,2]}' "$STDOUT"
    run_shell "$shell" '. "$1" || exit 10; printf "{nope" | agent_json >/dev/null 2>&1; exit $?' x
    assert_same 'nonzero' "$([ "$STATUS" -ne 0 ] && echo nonzero || echo zero)"
  done
}

function test_agent_codepoints_exposes_invisible_characters() {
  command -v perl >/dev/null || return 0
  local shell
  for shell in $(available_shells); do
    run_shell "$shell" '. "$1" || exit 10; agent_codepoints "$(printf "a\342\200\213\303\251")"' x
    assert_same "$(printf 'U+0061\ta\nU+200B\tCf\nU+00E9\té')" "$STDOUT"
  done
}

function test_agent_php_lint_reports_failures_and_skips_vendor() {
  command -v php >/dev/null || return 0
  local shell tree="$TEST_ROOT/php tree"
  mkdir -p "$tree/src" "$tree/vendor"
  printf '<?php echo 1;\n' > "$tree/src/ok.php"
  for shell in $(available_shells); do
    run_shell "$shell" '. "$1" || exit 10; agent_php_lint "$2"' "$tree"
    assert_same '0' "$STATUS"
    assert_contains '1 ok, 0 with errors' "$STDOUT"
  done
  printf '<?php echo ;\n' > "$tree/src/bad.php"
  printf '<?php echo ;\n' > "$tree/vendor/skipped.php"
  for shell in $(available_shells); do
    run_shell "$shell" '. "$1" || exit 10; agent_php_lint "$2"' "$tree"
    assert_same '1' "$STATUS"
    assert_contains 'bad.php' "$STDOUT"
    assert_contains '1 ok, 1 with errors' "$STDOUT"
    assert_same 'absent' "$(case "$STDOUT" in *skipped.php*) echo present ;; *) echo absent ;; esac)"
  done
}

function test_agent_extract_is_safe_and_keeps_the_archive() {
  local shell src="$TEST_ROOT/src" archive="$TEST_ROOT/pack.tar.gz"
  mkdir -p "$src/dir"
  printf 'content\n' > "$src/dir/file.txt"
  tar -czf "$archive" -C "$src" dir
  for shell in $(available_shells); do
    rm -rf -- "$TEST_ROOT/out"
    run_shell "$shell" '. "$1" || exit 10; agent_extract "$2" "$3"' "$archive" "$TEST_ROOT/out"
    assert_same '0' "$STATUS"
    assert_same 'content' "$(cat "$TEST_ROOT/out/dir/file.txt")"
    assert_same 'present' "$([ -f "$archive" ] && echo present || echo absent)"
    run_shell "$shell" '. "$1" || exit 10; agent_extract "$2" "$3"' "$archive" "$TEST_ROOT/out"
    assert_same '1' "$STATUS"
    run_shell "$shell" '. "$1" || exit 10; agent_extract "$2" "$3"' "$TEST_ROOT/src/dir/file.txt" "$TEST_ROOT/o2"
    assert_same '64' "$STATUS"
  done
  python3 -c 'import sys, tarfile
with tarfile.open(sys.argv[1], "w") as t: t.add(sys.argv[2], arcname="../evil.txt")' "$TEST_ROOT/evil.tar" "$src/dir/file.txt"
  for shell in $(available_shells); do
    run_shell "$shell" '. "$1" || exit 10; agent_extract "$2" "$3"' "$TEST_ROOT/evil.tar" "$TEST_ROOT/o3"
    assert_same '2' "$STATUS"
    assert_same 'absent' "$([ -e "$TEST_ROOT/o3" ] && echo present || echo absent)"
  done
}

function test_agent_context_reports_php_project_facts_without_running_scripts() {
  command -v jq >/dev/null || return 0
  local shell proj="$TEST_ROOT/php-project" bin
  mkdir -p "$proj/vendor/bin" "$TEST_ROOT/no-php" "$TEST_ROOT/with-php"
  git init -q "$proj"
  printf '{"name":"example/project","require":{"php":">=8.2"},"scripts":{"test":"touch %s/ran && phpunit"}}\n' "$TEST_ROOT" > "$proj/composer.json"
  touch "$proj/phpunit.xml.dist" "$proj/.editorconfig" "$proj/vendor/bin/phpunit"
  chmod +x "$proj/vendor/bin/phpunit"
  for bin in git jq; do
    ln -s "$(command -v "$bin")" "$TEST_ROOT/no-php/$bin"
    ln -s "$(command -v "$bin")" "$TEST_ROOT/with-php/$bin"
  done
  printf '#!/bin/sh\nexit 0\n' > "$TEST_ROOT/with-php/php"
  chmod +x "$TEST_ROOT/with-php/php"
  for shell in $(available_shells); do
    run_shell "$shell" '. "$1" || exit 10; cd "$2" && PATH="$3" agent_context' "$proj" "$TEST_ROOT/no-php"
    assert_same '0' "$STATUS"
    assert_contains 'Package: example/project' "$STDOUT"
    assert_contains 'PHP constraint: >=8.2' "$STDOUT"
    assert_contains 'phpunit.xml.dist' "$STDOUT"
    assert_contains 'vendor/bin/phpunit' "$STDOUT"
    assert_contains 'Cannot run these checks: PHP is unavailable.' "$STDOUT"
    run_shell "$shell" '. "$1" || exit 10; cd "$2" && PATH="$3" agent_context' "$proj" "$TEST_ROOT/with-php"
    assert_same 'absent' "$(case "$STDOUT" in *'PHP is unavailable'*) echo present ;; *) echo absent ;; esac)"
    assert_same 'absent' "$([ -e "$TEST_ROOT/ran" ] && echo present || echo absent)"
  done
  printf '{invalid json\n' > "$proj/composer.json"
  run_shell bash '. "$1" || exit 10; cd "$2" && agent_context >/dev/null 2>&1; exit $?' "$proj"
  assert_same 'nonzero' "$([ "$STATUS" -ne 0 ] && echo nonzero || echo zero)"
}

function test_agent_diff_matches_native_git_and_navigation_helpers_work() {
  local shell repo="$TEST_ROOT/diff repo [λ]"
  git init -q "$repo"
  printf 'before\n' > "$repo/text.txt"
  git -C "$repo" add text.txt
  git -C "$repo" -c user.name=t -c user.email=t@example.test commit -qm fixture
  printf 'after \n' > "$repo/text.txt"
  mkdir -p "$repo/sub"
  git -C "$repo" --no-pager -c color.ui=false diff --no-ext-diff --no-textconv > "$TEST_ROOT/native.diff"
  for shell in $(available_shells); do
    run_shell "$shell" '. "$1" || exit 10; cd "$2" && agent_diff' "$repo"
    assert_same "$(cat "$TEST_ROOT/native.diff")" "$STDOUT"
    run_shell "$shell" '. "$1" || exit 10; cd "$2" && agent_diff_check >/dev/null; exit $?' "$repo"
    assert_same '2' "$STATUS"
    run_shell "$shell" '. "$1" || exit 10; cd "$2/sub" && agent_root && pwd -P' "$repo"
    assert_same "$(cd -P "$repo" && pwd -P)" "$STDOUT"
    run_shell "$shell" '. "$1" || exit 10; agent_mkcd "$2/-new dir" && pwd -P' "$TEST_ROOT"
    assert_same "$TEST_ROOT/-new dir" "$STDOUT"
    rm -rf -- "$TEST_ROOT/-new dir"
    run_shell "$shell" '. "$1" || exit 10; agent_mkcd; exit $?' x
    assert_same '2' "$STATUS"
  done
}
