#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

command -v jq >/dev/null || { printf '%s\n' 'jq is required' >&2; exit 77; }
source "$repo_root/.aliases"

mkdir "$tmp/php-project"
git -C "$tmp/php-project" init -q
cat >"$tmp/php-project/composer.json" <<'JSON'
{
  "name": "example/project",
  "require": {"php": ">=8.2"},
  "scripts": {"test": "touch $AGENT_CONTEXT_MARKER && phpunit"}
}
JSON
touch "$tmp/php-project/phpunit.xml.dist" "$tmp/php-project/.editorconfig"
mkdir -p "$tmp/php-project/vendor/bin"
touch "$tmp/php-project/vendor/bin/phpunit"
chmod +x "$tmp/php-project/vendor/bin/phpunit"
export AGENT_CONTEXT_MARKER="$tmp/script-ran"

output=$(cd "$tmp/php-project" && agent_context)
[[ "$output" == *'PHP / Composer project:'* ]]
[[ "$output" == *'Package: example/project'* ]]
[[ "$output" == *'PHP constraint: >=8.2'* ]]
[[ "$output" == *'test: touch $AGENT_CONTEXT_MARKER && phpunit'* ]]
[[ "$output" == *'phpunit.xml.dist'* && "$output" == *'.editorconfig'* ]]
[[ "$output" == *'vendor/bin/phpunit'* ]]
[[ ! -e "$AGENT_CONTEXT_MARKER" ]]

mkdir "$tmp/plain-project"
git -C "$tmp/plain-project" init -q
output=$(cd "$tmp/plain-project" && agent_context)
[[ "$output" != *'PHP / Composer project:'* ]]

printf '{invalid json\n' >"$tmp/php-project/composer.json"
if (cd "$tmp/php-project" && agent_context >"$tmp/invalid.out" 2>"$tmp/invalid.err"); then
    printf '%s\n' 'Expected malformed composer.json to fail' >&2
    exit 1
fi
[[ -s "$tmp/invalid.err" ]]

printf '%s\n' 'project_context_test.sh: passed'
