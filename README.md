# agent-dotfiles

**Bash/Zsh dotfiles and evidence-preserving CLI helpers for coding agents.**

Inspired by [voku/dotfiles](https://github.com/voku/dotfiles), reworked for
non-interactive coding workflows: explicit activation, namespaced functions,
exact source evidence and no prompt hooks or startup-file edits. Python 3.10+
standard-library code supplies stable JSON; Git and ripgrep supply native evidence.
This source prepares **0.4.0** with the Bash/Zsh setup. The
[published releases](https://github.com/voku/agent-dotfiles/releases) record which
versions have shipped. Install only from an independently approved full commit.

Use native tools for simple, known-location questions; select these helpers when
source identity, literal scope or explicit completeness improves the evidence.
See [tool selection](docs/SHELL.md#choose-tools-by-the-evidence-needed).
[Fresh owner-capability dogfood](docs/MOMENTUM_EXPERIMENTS.md) records actual
bootstrap, discovery and guidance-maintenance probes, including their limits.

## Quick start

Use the checkout directly, without installation:

```bash
# Bash: explicit activation in the current shell
source /path/to/agent-dotfiles/.bashrc
agent_doctor
agent_search 'function save(' --root /path/to/project --glob '*.php'
agent_read src/Service.php --root /path/to/project --start 80 --end 180
agent_status --root /path/to/project
agent_dotfiles workspace --root /path/to/project
agent_patch src/Service.php --root /path/to/project --base HEAD~1
agent_deactivate
```

Zsh users source `/path/to/agent-dotfiles/.zshrc` instead. Neither profile changes
PATH, shell options, the current directory, prompts, user dotfiles or Git config.
For a non-interactive agent session, use `env -u BASH_ENV bash --noprofile --norc` or `zsh -f`
and explicitly source the reviewed profile. See [shell setup and helpers](docs/SHELL.md).

For a reusable consumer, preview the exact planned files and hashes, then
install a reviewed full commit into a private prefix:

```sh
./install.sh plan --prefix /existing/private/agent-tools --revision APPROVED_FULL_COMMIT_SHA
./install.sh --prefix /existing/private/agent-tools --revision APPROVED_FULL_COMMIT_SHA
./install.sh verify --prefix /existing/private/agent-tools --revision APPROVED_FULL_COMMIT_SHA
```

Then source the installed `/existing/private/agent-tools/.bashrc` or `.zshrc`
in a fresh consumer shell. Replace the placeholders with your approved pin and
actual absolute path. [Installation and rollback](docs/INSTALLATION.md) explains
verification and safe removal. No package installation or network download occurs.

## Layout

```text
.bashrc              explicit Bash activation
.zshrc               explicit Zsh activation
.shellrc             shared root resolution and reviewed lifecycle loader
.exports             agent-owned installation location
.functions           fixed-module loader and deactivation
shell/core/          fixed activation and deactivation lifecycle
shell/modules/       explicit context and Git helper definitions
install.sh           pinned install / verify / uninstall entrypoint
bin/agent-dotfiles   standalone machine-readable CLI
agent_dotfiles/      Python standard-library implementation
tools/install.py    verified private-prefix installer
tests/               contracts and real shell/Git integration
docs/                concise contracts, examples and historical evidence links
```

## What works now

- Read-only `doctor` inventory for `rg`, `git`, `jq`, `fd`/`fdfind`, `shellcheck`, `strace`, `hyperfine`.
- Bounded file discovery, using direct `rg --files --null` by default or explicit `fd`/`fdfind`.
- Bounded Git status, using `git status --porcelain=v1 -z` with rename/copy paths decoded in order.
- Read-only `workspace` identity: canonical Git checkout root, HEAD, branch/detached state, local tool path/version and bounded original status entries. The requested root must belong to the reported checkout; inherited `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE` overrides are refused. HEAD is checked before and after the scan, but the worktree scan is not atomic; truncated status exits 3 and never claims a clean tree. Unavailable HEAD and invalid repository roots produce distinct errors. The reported tool path is not a verified installation signature.
- Bounded text search, using `rg --json` and literal matching by default. Original `rg` match records are preserved, including byte-encoded paths and lines. Explicit `--path` / repeatable `--glob` can narrow a question without truncating original matches.
- Exact UTF-8 `read` ranges with original whitespace/newlines, EOF metadata and SHA-256 of the whole file. No ellipses.
- Index-only `tracked` listing (`git ls-files -z`) with correct handling of unusual paths.
- Exact `git-patch` for one path using Git binary/full-index diff, SHA-256 and an error if output cannot fit; no replacement with diffstat.
- Stable JSON envelopes and explicit result limits. Search respects `.gitignore` by default; `--hidden` is opt-in.
- Runtime commands do not install anything, access the network or load shell startup files. A separate, explicit installer supports pinned private prefixes, verification and safe removal.

See [shell helpers](docs/SHELL.md), [pinned installation and rollback](docs/INSTALLATION.md) and the [optional agent-loop consumer contract](docs/AGENT_LOOP.md). Automatic installation and host-policy changes remain outside the CLI contract.

## Requirements

Python 3.10+ on Linux, macOS or WSL, and `rg` for the search commands. `git` is recommended for coding workflows. Everything else is optional. The name `sg` is deliberately not recognized as `ast-grep`, because on Linux it can refer to the unrelated `newgrp` utility. The Python standard library is sufficient; no pip/Composer install is required.

## Usage

From the checkout:

```sh
./bin/agent-dotfiles doctor
./bin/agent-dotfiles doctor --strict
./bin/agent-dotfiles files --root . --limit 50
./bin/agent-dotfiles git-status --root . --limit 50
./bin/agent-dotfiles workspace --root . --limit 50
./bin/agent-dotfiles files --engine fd --limit 50 # explicit alternative; different semantics
./bin/agent-dotfiles search 'function save(' --root . --limit 20
./bin/agent-dotfiles search '^final class ' --regex --limit 20
./bin/agent-dotfiles search 'save(' --path src --glob '*.php' --limit 30
./bin/agent-dotfiles tracked --limit 100
./bin/agent-dotfiles read src/Service.php --start 80 --end 180
./bin/agent-dotfiles git-patch src/Service.php --base HEAD~1
```

All **successful** commands print one JSON object to stdout. There is no pager or color output.

| Exit code | Meaning |
| --- | --- |
| 0 | Complete success; doctor reports inventory even when tools are missing unless `--strict` |
| 1 | Search completed with zero matches |
| 2 | Explicit error: invalid arguments, missing tool, bad output, timeout, or subprocess failure; doctor `--strict` also uses 2 |
| 3 | **Truncated**: more records than `--limit`, or output byte cap exceeded. Treat results as incomplete. |

Output schemas: `agent-dotfiles.v1.doctor`, `agent-dotfiles.v1.files`, `agent-dotfiles.v1.git-status`, `agent-dotfiles.v1.workspace`, `agent-dotfiles.v1.search`, `agent-dotfiles.v1.tracked`, `agent-dotfiles.v1.read`, `agent-dotfiles.v1.git-patch`, `agent-dotfiles.v1.error`. An exact `read` or `git-patch` command **fails** if the requested content would exceed the cap. It never returns a shortened source or patch. A result with `truncated: true` must **never** be presented as a complete repository search. Limits default to 100, maximum 1000; process output is limited to 2 MiB and wall time to 20 seconds.

### Source of truth

Use the right tool for the *question*, not the shortest alias:

| Task | Preferred tool |
| --- | --- |
| Literal text/config/templates | `rg` or bounded `agent-dotfiles search` |
| File paths | `rg --files -0` or bounded `agent-dotfiles files` |
| Tracked files | `git ls-files -z` |
| Worktree changes | `git status --porcelain=v1 -z` |
| JSON transformation | `jq`, with explicit filters and exit handling |
| PHP definitions/callers/impact | `agent-loop map` when available and fresh; verify source ranges |
| Shell static analysis | `shellcheck` where installed |
| Runtime diagnosis | `strace` only for a scoped Linux investigation |
| CLI comparison | `hyperfine` only for measured experiments |

See [Context-first policy](docs/CONTEXT_POLICY.md), [Git evidence and opt-in aliases](docs/GIT_CONTEXT.md), [Tool matrix](docs/TOOL_MATRIX.md), [Security](docs/SECURITY.md) and [Agent Loop boundary](docs/AGENT_LOOP.md).

## Why not an output-compression proxy?

This tool does **not** intercept `git diff`, `rg`, PHPStan, tests or shell tools.
The `snip`-style `git diff` → `--stat` substitution could omit precisely the
code being reviewed, even though the token count looks attractive. Bounded
*navigation* is explicit; a selected file or patch is delivered without lossy
transformation. Optimization is evaluated on correct completed tasks, total
latency and retries, not savings percentages.

## Tests: Python contracts + Bashunit integration

The Python unittest contracts remain authoritative for internal parsing,
path safety, byte preservation and failure handling. Bashunit 0.50.1 adds
**end-to-end shell/CLI tests** for actual executable behavior and exit codes;
it does not replace the Python tests with lossy snapshots.

```sh
python3 -m compileall -q agent_dotfiles bin tests tools
python3 -m unittest discover -s tests -v
# After installing/pinning bashunit 0.50.1 separately:
bashunit test tests/shell --strict
```

GitHub CI installs Bashunit via an immutable, SHA-pinned official action with
checksum verification. Nothing is installed by running `agent-dotfiles`.


The tests use fake command executables to verify result contracts without depending on system-specific versions, interactive dotfiles, networking, or external package installations.

## GitHub workflow

The repository is now maintained at [voku/agent-dotfiles](https://github.com/voku/agent-dotfiles).
Development uses reviewable feature branches, tests, and pull requests. Its
original repository-creation helper has been removed: it is not suitable for
updating an existing GitHub repository. No command silently publishes changes,
merges branches or changes the agent's global configuration.

[Governed PHP maintenance and evidence-quality cycle](docs/QUALITY_CYCLE_17.md): independently scored repairs, Dream review, owner correction and honest limits.
