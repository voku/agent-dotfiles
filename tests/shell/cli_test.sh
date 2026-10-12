#!/usr/bin/env bash
# bashunit integration tests: real entrypoint/exit codes and exact evidence.
# Python unittest remains the owner of deep output-parser contracts.

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
CLI="$PROJECT_ROOT/bin/agent-dotfiles"

function set_up() {
  TEST_ROOT="$(mktemp -d)"
}

function tear_down() {
  rm -rf -- "$TEST_ROOT"
}

function test_doctor_returns_valid_json_without_shell_changes() {
  local output status result
  output="$(python3 "$CLI" doctor)"
  status=$?
  assert_same '0' "$status"
  result="$(printf '%s' "$output" | python3 -c 'import json,sys; x=json.load(sys.stdin); print(x["schema"]+" "+str(x["installation_performed"]).lower()+" "+str(x["shell_startup_loaded"]).lower())')"
  assert_same 'agent-dotfiles.v1.doctor false false' "$result"
}

function test_missing_source_is_explicit_error_not_empty_success() {
  local output status result
  # Under bashunit --strict, a deliberate nonzero exit must be handled within an if.
  if output="$(python3 "$CLI" read absent.php --root "$TEST_ROOT")"; then
    status=0
  else
    status=$?
  fi
  assert_same '2' "$status"
  result="$(printf '%s' "$output" | python3 -c 'import json,sys; x=json.load(sys.stdin); print(x["schema"]+" "+x["error"])')"
  assert_same 'agent-dotfiles.v1.error invalid_file' "$result"
}

function test_read_returns_exact_long_line_and_digest() {
  local output status result
  python3 - "$TEST_ROOT" <<'PYDATA'
from pathlib import Path
import sys
Path(sys.argv[1], 'source file.php').write_text('a' * 400 + '\nsecond line\n', encoding='utf-8')
PYDATA
  output="$(python3 "$CLI" read 'source file.php' --root "$TEST_ROOT" --start 1 --end 2)"
  status=$?
  assert_same '0' "$status"
  result="$(printf '%s' "$output" | python3 -c 'import hashlib,json,sys; x=json.load(sys.stdin); s="a"*400+"\nsecond line\n"; print(int(x["content"]==s), int(x["sha256"]==hashlib.sha256(s.encode()).hexdigest()), x["truncated"])')"
  assert_same '1 1 False' "$result"
}

function test_real_git_status_preserves_newline_filename() {
  local output status result
  git init -q "$TEST_ROOT"
  printf 'test\n' > "$TEST_ROOT/with newline
file.php"
  output="$(python3 "$CLI" git-status --root "$TEST_ROOT")"
  status=$?
  assert_same '0' "$status"
  result="$(printf '%s' "$output" | python3 -c 'import json,sys; x=json.load(sys.stdin); print(x["schema"], len(x["changes"]), int(x["changes"][0]["path"]=="with newline\nfile.php"), x["truncated"])')"
  assert_same 'agent-dotfiles.v1.git-status 1 1 False' "$result"
}

function test_explicit_shell_workspace_helper_returns_real_receipt() {
  local output status result
  git init -q "$TEST_ROOT"
  printf 'baseline\n' > "$TEST_ROOT/source.php"
  git -C "$TEST_ROOT" add -- source.php
  git -C "$TEST_ROOT" -c user.email=test@example.test -c user.name=Test commit -qm baseline
  if output="$(env -u BASH_ENV bash --noprofile --norc -c '. "$1/.bashrc" || exit $?; agent_workspace --root "$2"' consumer "$PROJECT_ROOT" "$TEST_ROOT")"; then
    status=0
  else
    status=$?
  fi
  assert_same '0' "$status"
  result="$(printf '%s' "$output" | python3 -c 'import json,sys; x=json.load(sys.stdin); print(x["schema"], x["root"], x["truncated"])')"
  assert_same "agent-dotfiles.v1.workspace $TEST_ROOT False" "$result"
}

function test_git_patch_is_full_patch_not_diffstat() {
  local output status result
  git init -q "$TEST_ROOT"
  printf 'alpha\n' > "$TEST_ROOT/source.php"
  git -C "$TEST_ROOT" add -- source.php
  git -C "$TEST_ROOT" -c user.email=test@example.test -c user.name=Test commit -qm baseline
  printf 'alpha\nbeta\n' > "$TEST_ROOT/source.php"
  output="$(python3 "$CLI" git-patch source.php --root "$TEST_ROOT")"
  status=$?
  assert_same '0' "$status"
  result="$(printf '%s' "$output" | python3 -c 'import hashlib,json,sys; x=json.load(sys.stdin); p=x["patch"]["text"]; print(int("+beta" in p), int("diff --git" in p), int(hashlib.sha256(p.encode()).hexdigest()==x["sha256"]), x["truncated"])')"
  assert_same '1 1 1 False' "$result"
}

function test_source_checkout_has_no_automatic_publish_or_install() {
  assert_file_exists "$PROJECT_ROOT/config/gitconfig.agent.example"
  assert_file_not_exists "$PROJECT_ROOT/scripts/publish.sh"
  assert_file_exists "$PROJECT_ROOT/agent_dotfiles/cli.py"
}
