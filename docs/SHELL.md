# Agent shell environment

The layout follows [voku/dotfiles](https://github.com/voku/dotfiles) (`.exports`,
`.functions`, `.redpill/`), but its content is for non-interactive coding
agents: no prompt, history, completion, plugin or theme code, and nothing that
runs unless you source it.

| File | Purpose |
| --- | --- |
| `.bashrc` / `.zshrc` | Explicit entry points; refuse the wrong shell; never read user startup files |
| `.shellrc` | Resolves the checkout root, then calls `.redpill/lib/activation.sh` |
| `.exports` | `AGENT_DOTFILES_HOME`; applies `agent.env` and `RIPGREP_CONFIG_PATH` |
| `.functions` | the `agent_*` helpers below |
| `.redpill/lib/` | Activation preflight and `agent_deactivate` |
| `.redpill/config/` | `agent.env` (CLI settings), `ripgreprc`, opt-in `gitignore_global` and `wgetrc` |

There is no `.aliases`: aliases do not expand in non-interactive shells, so
every helper is a function and behaves the same in Bash and Zsh.

## Activate

```sh
env -u BASH_ENV bash --noprofile --norc    # or: zsh -f
source /absolute/path/to/agent-dotfiles/.bashrc   # .zshrc in Zsh
agent_git -C /project status --short
agent_deactivate
```

Clear `BASH_ENV` yourself: Bash reads it before any profile runs. Activation is
silent, keeps `PATH`, working directory, shell options and positional arguments,
and refuses (exit 2, nothing exported) if a required file is missing, a name it
owns is already defined, or `AGENT_DOTFILES_HOME` exists.

## CLI settings

Agents do not need progress bars, color codes, banners, pagers, update nags or
prompts. `.redpill/config/agent.env` lists the environment variables that turn
these off, grouped per tool (generic, Git, Composer, Node, Python, Rust). It is
read as `NAME=value` data, never sourced. A name takes effect **only if the host
has not already exported it**, and `agent_deactivate` removes exactly the names
added, so `env` before activation equals `env` after deactivation. Nothing is
written to disk, Git config or user startup files. Detail per tool comes from
[awesome-ai-friendly-cli](https://github.com/alies-dev/awesome-ai-friendly-cli).

What is deliberately **not** set: `CI=true` (changes tool behavior, e.g. test
watch modes), `--quiet`-style switches, audit/vulnerability switches and
telemetry opt-outs. Settings remove noise; they never hide results, errors,
warnings or exit statuses.

To add a setting, add a `NAME=value` line to `agent.env` and a test if its
behavior is not already covered. `RIPGREP_CONFIG_PATH` is exported by `.exports`
because it depends on the checkout path.

### Flags that have no environment variable

Some tools only take flags. Use these in project commands (PHP shown; other
ecosystems are in the linked catalog):

```sh
vendor/bin/phpunit --no-progress --colors=never --display-errors --display-warnings
vendor/bin/phpstan analyse --no-progress --no-ansi --error-format=raw
vendor/bin/psalm --no-progress --no-suggestions --output-format=text
vendor/bin/phpcs --report=emacs -q --no-colors
vendor/bin/php-cs-fixer fix --show-progress=none --no-ansi -n
vendor/bin/rector process --no-progress-bar --no-ansi
composer install --no-progress --no-ansi -n
```

## Optional global gitignore

`.redpill/config/gitignore_global` lists editor and OS noise (`.idea/`, `.vscode/`,
`.DS_Store`). Activation never applies it, because that edits Git config. Opt in
once, yourself:

```sh
git config --global core.excludesFile /absolute/path/to/agent-dotfiles/.redpill/config/gitignore_global
```

## Optional wget settings

`.redpill/config/wgetrc` bounds waits (`timeout`, `tries`, `retry_connrefused`)
and prints server responses. Wget only reads it through `WGETRC`, which would
replace the user's own `~/.wgetrc`, so it is never exported for you:

```sh
WGETRC="/absolute/path/to/agent-dotfiles/.redpill/config/wgetrc" wget URL
```

## Known behavior

- **Symlinked profiles are refused** (exit 2, `.shellrc is missing or unreadable`):
  the root is the physical directory of the sourced file. Source the real path.
- **Child shells inherit variables, not functions.** A `bash -c` started by a tool
  sees `PAGER=cat` but has no `agent_git`; source the profile there too.
- **`rg` output order changes between identical runs** (parallel walk). Compare
  results as sets, or add `--sort path` when a stable order matters.

## Never cut output silently

Half of the shell calls in the friction log end in `| head`, which drops the
rest without a word. Use the announcing form, and prefer a count when the
question is "how many":

```sh
agent_rg -n 'pattern' src | agent_head 50     # prints "TRUNCATED, showed 50 of 812 lines"
agent_rg -c 'pattern' src                     # per-file counts, nothing cut
```

## Helpers

- `agent_git` – `git --no-pager -c color.ui=false` with prompts off; full output and exit status.
- `agent_rg` – `rg --no-config --color=never`, immune to host ripgrep config. Exit 1 means no match; 2 is an error.
- `agent_curl` – `curl --silent --show-error --location`: no progress meter, errors and redirects handled.
- `agent_require TOOL [MIN]` – capability check: prints `tool<TAB>version<TAB>path`. Exit 1 missing, 2 too old, 3 version unreadable, 64 usage. Runs `TOOL --version`.
- `agent_head [N]` – first N lines (default 100) of stdin, then `agent_head: TRUNCATED, showed N of M lines` on stdout. Use it instead of a bare `head`, which truncates silently.
- `agent_usage [DIR]` – `du -h -d 1`.
- `agent_codepoints STRING` – one `U+XXXX<TAB>char` line per character; invisible ones (control, format, space) show their category, to find zero-width characters and lookalike spaces.
- `agent_php_lint [DIR]` – parallel `php -l` over `*.php`, skipping `.git`, `vendor` and `node_modules`. Reports files with errors plus ok/error/unchecked counts; any error or unchecked file makes the command fail.
- `agent_extract ARCHIVE DEST` – unpack tar(.gz/.bz2/.xz) or zip into a new or empty DEST. Keeps the archive, refuses absolute or `..` entries (exit 2). Entries are listed, not otherwise vetted: review untrusted archives before use.
- `agent_context` – orientation for a task: repo root, `status --short --branch`, staged and unstaged `--stat`, and for a Composer project the package, PHP constraint, declared scripts, config files, available `php`/`composer` and installed `vendor/bin` checks. Reads `composer.json` with `jq`; never runs a script.
- `agent_diff [ARGS]`, `agent_diff_check` – complete native patch with external diff drivers off; `git diff --check` for staged and unstaged changes.
- `agent_root`, `agent_mkcd DIR` – `cd` to the repository root; `mkdir -p` and `cd` (safe for spaces and leading dashes). These change the current shell's directory; they shadow nothing.
- `agent_history`, `agent_blame` – native `git log` / `git blame --line-porcelain` with `--literal-pathspecs`.

No helper shadows `git`, `rg`, `cd` or any other native command.

## Test

```sh
bashunit test tests/shell --strict
```

Adding a helper: define `agent_name() { ...` in `.functions` with the name at
the start of a line. Activation derives the owned namespace (collision check)
from those definitions and `agent_deactivate` removes exactly them, so there is
no second list to update. Add a test to `tests/shell/activation_test.sh`.
