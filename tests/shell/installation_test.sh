#!/usr/bin/env bash
# Real pinned install/consumer/rollback, without global activation.
INSTALL_PROJECT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"

function set_up() {
  INSTALL_TEST_ROOT="$(mktemp -d)"
  python3 - "$INSTALL_PROJECT" "$INSTALL_TEST_ROOT/source" <<'PY'
from pathlib import Path
import shutil, sys
source, fixture = map(Path, sys.argv[1:])
fixture.mkdir()
for name in ('agent_dotfiles', 'bin', '.redpill', 'skills', 'profiles'):
    shutil.copytree(source / name, fixture / name, ignore=shutil.ignore_patterns('__pycache__'))
for name in ('LICENSE', '.bashrc', '.zshrc', '.shellrc', '.functions', '.exports', '.aliases'):
    shutil.copyfile(source / name, fixture / name)
PY
  git init -q "$INSTALL_TEST_ROOT/source"
  git -C "$INSTALL_TEST_ROOT/source" add .
  git -C "$INSTALL_TEST_ROOT/source" -c user.name=Fixture -c user.email=fixture@example.invalid commit -qm fixture
  INSTALL_TEST_PIN="$(git -C "$INSTALL_TEST_ROOT/source" rev-parse HEAD)"
}

function tear_down() {
  rm -rf -- "$INSTALL_TEST_ROOT"
}

function test_pinned_install_consumer_verify_and_rollback() {
  local output
  output="$(python3 "$INSTALL_PROJECT/tools/install.py" install --source "$INSTALL_TEST_ROOT/source" --revision "$INSTALL_TEST_PIN" --prefix "$INSTALL_TEST_ROOT/consumer")"
  assert_same 'true' "$(printf '%s' "$output" | python3 -c 'import json,sys; print(str(json.load(sys.stdin)["ok"]).lower())')"
  output="$("$INSTALL_TEST_ROOT/consumer/bin/agent-dotfiles" doctor)"
  assert_same 'agent-dotfiles.v1.doctor' "$(printf '%s' "$output" | python3 -c 'import json,sys; print(json.load(sys.stdin)["schema"])')"
  python3 "$INSTALL_PROJECT/tools/install.py" verify --prefix "$INSTALL_TEST_ROOT/consumer" --revision "$INSTALL_TEST_PIN" >/dev/null
  python3 "$INSTALL_PROJECT/tools/install.py" uninstall --prefix "$INSTALL_TEST_ROOT/consumer" --revision "$INSTALL_TEST_PIN" >/dev/null
  assert_directory_not_exists "$INSTALL_TEST_ROOT/consumer"
}

function test_modified_consumer_is_preserved_on_removal_refusal() {
  local output status
  python3 "$INSTALL_PROJECT/tools/install.py" install --source "$INSTALL_TEST_ROOT/source" --revision "$INSTALL_TEST_PIN" --prefix "$INSTALL_TEST_ROOT/consumer" >/dev/null
  printf '# retained local change\n' > "$INSTALL_TEST_ROOT/consumer/agent_dotfiles/__init__.py"
  if output="$(python3 "$INSTALL_PROJECT/tools/install.py" uninstall --prefix "$INSTALL_TEST_ROOT/consumer")"; then
    status=0
  else
    status=$?
  fi
  assert_same '2' "$status"
  assert_file_exists "$INSTALL_TEST_ROOT/consumer/agent_dotfiles/__init__.py"
  assert_same '# retained local change' "$(cat "$INSTALL_TEST_ROOT/consumer/agent_dotfiles/__init__.py")"
}

function test_installed_bash_helpers_preserve_source_and_safe_deactivation() {
  local output
  python3 "$INSTALL_PROJECT/tools/install.py" install --source "$INSTALL_TEST_ROOT/source" --revision "$INSTALL_TEST_PIN" --prefix "$INSTALL_TEST_ROOT/consumer" >/dev/null
  printf 'first\nsecond\n' > "$INSTALL_TEST_ROOT/literal [λ].txt"
  output="$(env -u BASH_ENV bash --noprofile --norc -c '. "$1/.bashrc"; agent_read "$2" --root "$3" --start 2 --end 2; agent_deactivate' consumer "$INSTALL_TEST_ROOT/consumer" 'literal [λ].txt' "$INSTALL_TEST_ROOT")"
  assert_same 'second' "$(printf '%s' "$output" | python3 -c 'import json,sys; print(json.load(sys.stdin)["content"], end="")')"
  python3 "$INSTALL_PROJECT/tools/install.py" verify --prefix "$INSTALL_TEST_ROOT/consumer" --revision "$INSTALL_TEST_PIN" >/dev/null
}
