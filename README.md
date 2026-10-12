# agent-dotfiles

**A safe, optional shell environment for coding agents.**

The product is a reviewed shell environment for the tools agents already use:
`git`, `rg`, `grep`, `sed` and the project's developer tools. Its `.redpill/`
runtime provides explicit Bash/Zsh entry points and optional per-command presets.
The Python CLI remains an optional evidence/diagnostic API for coordinates,
whole-file hashes and explicit completeness; agents do not need to learn its
commands to do ordinary development work.

It takes inspiration from [voku/dotfiles](https://github.com/voku/dotfiles),
but is designed for non-interactive agents: no prompt hooks, startup-file edits,
package installation, global Git changes, or automatic activation.

## Start safely

Use a reviewed checkout directly. First inspect the small, fixed host-tool
baseline; this is read-only and prints a JSON plan rather than installing
anything:

```sh
./firstInstall.sh plan
```

It recommends only missing tools from the selected profile and leaves any
package action for explicit review. See [the first-install plan](docs/FIRST_INSTALL.md).

The default `doctor` inventory already includes the universal Git and search
baseline. No `minimal`, `git` or `shell` profile selection is needed for
coding or administration work. Their existing `--profile` names remain
available as backwards-compatible diagnostic views, not activation modes.

```sh
./bin/agent-dotfiles doctor
./bin/agent-dotfiles doctor --profile php
```

The optional PHP diagnostic checks whether `php` is available (required for
PHP work) and whether `composer` is available (useful but not mandatory for
every PHP project). A diagnostic never runs these discovered executables.

Start with familiar native commands, scoped to the actual project and file:

```sh
git --no-pager -c color.ui=false -C /project status --short
rg --no-config -n --color=never -F -- 'function save(' /project
sed -n '20,60p' /project/src/example.php
git --no-pager -c color.ui=false -C /project diff --no-ext-diff --no-textconv -- src/example.php
```

These invocations preserve native stdout, stderr and exit status. Use structured
output where the tool and task support it (`rg --json`, Git porcelain), rather
than assuming every command benefits from a JSON wrapper. Patches, source ranges
and failing-test details must remain complete. No measured token/time advantage
is claimed for a compact format.

The existing optional presets can be used in an explicit, temporary shell:

```sh
source /absolute/path/to/agent-dotfiles/.bashrc
agent_git -C /absolute/path/to/project status --short
agent_rg -n -F -- 'function save(' /absolute/path/to/project
agent_deactivate
```

Use `.zshrc` in Zsh. In a fresh non-interactive shell, start Bash with
`env -u BASH_ENV bash --noprofile --norc` or Zsh with `zsh -f`, then explicitly
source the reviewed profile. The [shell contract](docs/SHELL.md) describes the
namespaced helpers, exit statuses, and activation guarantees.

The familiar `.exports`, `.functions`, and `.aliases` entry points are adapted
for agents: `.exports` identifies only the selected runtime; `.functions` loads
a fixed reviewed module list; and `.aliases` contains portable named commands
instead of fragile interactive aliases. No command overrides `git` or `rg`.

## Pick the smallest useful tool

| Question | Recommended path |
| --- | --- |
| You know the file and only need a quick answer | Native `rg`, `git`, or a source read |
| You need match coordinates and explicit completeness | `agent-dotfiles search` or `agent_search` |
| You need exact lines tied to a file identity | `agent-dotfiles read` or `agent_read` |
| You need the complete patch for one literal file | `agent-dotfiles git-patch` or `agent_patch` |
| You need a bounded checkout identity and current worktree state | `agent-dotfiles workspace` or `agent_workspace` |
| You need PHP symbols or callers | [agent-map](https://github.com/voku/agent-map) through the current agent-loop workflow |
| You need a capability/readiness report | `agent-dotfiles doctor` (add `--profile php` for PHP-specific readiness) |

The profile is optional. Do not rerun a successful native command just to use a
helper. Search output can be incomplete: exit code `3` and `truncated: true`
mean that you must narrow the scope or retrieve more evidence before reaching a
conclusion.

## Install a pinned consumer copy

Installation is optional. It copies an independently reviewed full Git commit to
a private prefix and verifies every installed payload file. First preview the
exact plan, then install and verify the same approved commit:

```sh
./install.sh plan --prefix /existing/private/agent-tools --revision APPROVED_FULL_COMMIT_SHA
./install.sh --prefix /existing/private/agent-tools --revision APPROVED_FULL_COMMIT_SHA
./install.sh verify --prefix /existing/private/agent-tools --revision APPROVED_FULL_COMMIT_SHA
```

The installer neither downloads packages nor edits user shell files. It has an
explicit rollback path. Read [installation and rollback](docs/INSTALLATION.md)
before using it in a consumer environment.

## What is included

- Bounded literal search and file discovery with explicit hidden/ignored scope.
- Exact UTF-8 source ranges with a whole-file SHA-256 digest.
- Filename-safe Git status, tracked inventory, workspace identity, and complete
  literal-file patches.
- Stable JSON envelopes, meaningful exit statuses, and visible truncation.
- Read-only capability discovery for native and optional tools, including
  `fd`/`fdfind`, `jq`, `curl`, `ShellCheck`, `strace`, and `hyperfine`.
- A common baseline plus opt-in PHP diagnostics; legacy `minimal`, `git`, and
  `shell` views remain available. None is an installer, plugin loader, alias,
  or automatic routing mechanism.
- A project-onboarding skill for PHP work plus a selected, pinned set of
  portable skills from [agent-skills](https://github.com/voku/agent-skills).

The CLI uses Python 3.10+ and the standard library. `rg` is required for search;
Git is recommended for repository evidence. Linux, macOS, and WSL are supported
within the documented contracts; Windows installation is not supported.

## Agent integrations

[Project onboarding](docs/PROJECT_ONBOARDING.md) explains the shared Codex and
Claude Code skill for a PHP failure or unfamiliar project. It gathers verified
Git, Composer, configuration, and source context without automatically running
project checks.

[Selected portable skills](docs/AGENT_SKILLS.md) explains the consumer projection
and the maintainer-only, locally pinned synchronization process. The canonical
portable guidance remains owned by
[voku/agent-skills](https://github.com/voku/agent-skills); this repository does
not become a second skill catalog.

[agent-loop integration](docs/AGENT_LOOP.md) documents the optional consumer
boundary. Agent-loop can start and govern work when this repository is absent.

## Evidence before claims

The project aims to improve context quality, not to make output shorter at the
expense of relevant evidence. Its small controlled evaluations so far establish
correctness for their tested tasks, but do **not** prove a general productivity,
time, or model-token benefit. See the [evaluation record](docs/EVALUATION_2026-10-11.md)
and [full-cycle evidence](docs/FULL_CYCLE.md) for methods and limits.

## Documentation and community

The [repository layout and ownership guide](docs/REPOSITORY_LAYOUT.md) separates
consumer-installed tools from source-only examples and documentation. See
[the product boundary](docs/decisions/0001-product-boundaries.md):
`agent-dotfiles` provides an optional execution environment; `agent-loop`
independently owns task workflow, Learning, Recall and memory. Neither
is installed or configured implicitly by the other.

This repository tracks short, reviewable [project memory](MEMORY.md) and
[decisions](docs/decisions/0002-agent-shell-and-memory.md) for its own agent-loop maintenance. Raw sessions
and run receipts remain local `.agent-loop/` state and are never installed for
consumers.

Start with the [documentation index](docs/README.md). The public project paths
are [contributing](CONTRIBUTING.md), [code of conduct](CODE_OF_CONDUCT.md),
[security reporting](docs/SECURITY.md), and [support](SUPPORT.md). The project
is available under the [MIT License](LICENSE).

## Validate a checkout

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q agent_dotfiles bin tests tools
/path/to/bashunit/bashunit test tests/shell --strict
```

The Python suite checks CLI contracts and documentation links. The Bashunit
suite exercises observable shell and Git behavior in real fixtures. GitHub
Actions runs the supported Python and shell matrix independently.
