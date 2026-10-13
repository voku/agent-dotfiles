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

git_bin=$(command -v git)
jq_bin=$(command -v jq)
mkdir "$tmp/no-php-bin" "$tmp/with-php-bin"
ln -s "$git_bin" "$tmp/no-php-bin/git"
ln -s "$jq_bin" "$tmp/no-php-bin/jq"
ln -s "$git_bin" "$tmp/with-php-bin/git"
ln -s "$jq_bin" "$tmp/with-php-bin/jq"
cat >"$tmp/with-php-bin/php" <<'PHP'
#!/usr/bin/env bash
exit 0
PHP
chmod +x "$tmp/with-php-bin/php"

output=$(cd "$tmp/php-project" && PATH="$tmp/no-php-bin" agent_context)
[[ "$output" == *'PHP / Composer project:'* ]]
[[ "$output" == *'Package: example/project'* ]]
[[ "$output" == *'PHP constraint: >=8.2'* ]]
[[ "$output" == *'test: touch $AGENT_CONTEXT_MARKER && phpunit'* ]]
[[ "$output" == *'phpunit.xml.dist'* && "$output" == *'.editorconfig'* ]]
[[ "$output" == *'vendor/bin/phpunit'* ]]
[[ "$output" == *'Cannot run these checks: PHP is unavailable.'* ]]
[[ ! -e "$AGENT_CONTEXT_MARKER" ]]

output=$(cd "$tmp/php-project" && PATH="$tmp/with-php-bin" agent_context)
[[ "$output" == *'vendor/bin/phpunit'* ]]
[[ "$output" != *'Cannot run these checks: PHP is unavailable.'* ]]
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
