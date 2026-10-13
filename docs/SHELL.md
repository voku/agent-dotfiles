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
| `.functions` | the four `agent_*` helpers below |
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
watch modes), `--quiet`-style switches, audit/vulnerability switches,
telemetry opt-outs and `PYTHONIOENCODING` (changes codec behavior, not
presentation). Settings remove noise; they never hide results, errors,
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
- **`rg` skips NUL-containing files in recursive search**, silently (see above).

## Contract of the helpers

Product boundary: [ADR 0004](decisions/0004-environment-vs-task-strategy.md).
A helper is the native command with host-config bleed or interactivity
removed, and nothing else (plus `agent_head`, below). Same arguments, output and exit status as the
native tool under a clean configuration. Native tools stay native.

- `agent_git` – `git --no-pager -c color.ui=false` with prompts off.
- `agent_rg` – `rg --no-config --color=never`, immune to host ripgrep config. Exit 1 means no match; 2 is an error.
- `agent_diff [ARGS]` – `git diff --no-ext-diff --no-textconv`, no pager, no color: the raw patch even under a host Git config that sets an external driver.
- `agent_head [N]` – **the one exception** (ADR 0004, evidence preservation): first N lines (default 100) of stdin, then `agent_head: TRUNCATED, showed N of M lines` on stdout. Use it instead of a bare `| head`, which cuts silently:
  `agent_rg -n 'pattern' src | agent_head 50`. It handles text lines, prints the banner on stdout, and reads all input to count it. It does not make a search complete.

No helper shadows `git`, `rg`, `cd` or any other native command.

## What the helpers do not do

Task strategy is out of scope and no helper here claims to solve it: which
tool to search with, whether a result is complete, cross-checking, binary-file
policy, linting, orientation or archive handling. That belongs in
[agent-skills](https://github.com/voku/agent-skills) guidance.

One consequence is documented because it was observed (#69, #70): `agent_rg`
is native ripgrep, so a recursive search silently skips a file containing a NUL
byte even when it is source code that matches (exit 0, no message). `agent_rg`
is therefore **not** an "every file" tool and adds no `--binary`. Whoever needs
a complete inventory chooses the method, for example `git grep -l -z -F` for
tracked files or `rg --binary`, and verifies it independently. The regression
test keeps the limitation as evidence.

Removed helpers (`agent_php_lint`, `agent_context`, `agent_extract`,
`agent_require`, `agent_curl`, `agent_history`, `agent_blame`, `agent_diff_check`,
`agent_root`, `agent_mkcd`, `agent_usage`, `agent_codepoints`) are recoverable
from tag `v0.7.0`; the ADR gives the evidence and reason for each, and the owner where the capability stays useful.

## Test

```sh
bashunit test tests/shell --strict
```

Adding a helper: define `agent_name() { ...` in `.functions` with the name at
the start of a line. Activation derives the owned namespace (collision check)
from those definitions and `agent_deactivate` removes exactly them, so there is
no second list to update. Add a test to `tests/shell/activation_test.sh`.
