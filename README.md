# agent-dotfiles

**A small, inspectable development environment for coding agents.**

`agent-dotfiles` helps a coding agent inspect an unfamiliar repository without
turning partial output into invented certainty. It provides explicit Bash/Zsh
profiles plus a small Python CLI for bounded search, exact source ranges,
file-scoped Git patches, repository state, and machine-readable capability
reports.

It takes inspiration from [voku/dotfiles](https://github.com/voku/dotfiles),
but is designed for non-interactive agents: no prompt hooks, startup-file edits,
package installation, global Git changes, or automatic activation.

`agent-dotfiles` supplies tools and an optional shell, **not a task workflow**.
A separately installed [agent-loop](docs/AGENT_LOOP.md) may run inside this
environment and independently owns sessions, reviews, Learning, Recall, and
project memory. Neither product installs or configures the other implicitly.

## Getting started: try it without installing

Use a reviewed checkout directly, with Python 3.10+, Git and optional `rg` for
search. You may clone the repository yourself, but the CLI does not fetch code,
install packages or change your host configuration. First inspect the host-tool
baseline; this is read-only and prints a JSON plan rather than installing
anything:

```sh
./firstInstall.sh plan
```

It recommends only missing tools from the selected profile and leaves any
package action for explicit review. See [the first-install plan](docs/FIRST_INSTALL.md).

The `minimal` runtime profile is the recommended next step: it reports only
the capabilities needed for the basic workflow and does not change the shell.

```sh
./bin/agent-dotfiles doctor --profile minimal
```

To try it against an **existing** project, without installing or activating
anything, replace the project path and invoke the CLI directly:

```sh
./bin/agent-dotfiles workspace --root /absolute/path/to/project --limit 50
./bin/agent-dotfiles search 'TODO' --root /absolute/path/to/project --limit 20
```

The `workspace` command needs a Git repository with at least one commit;
an unborn `HEAD` is an explicit error (not a fabricated workspace identity).
Search requires `rg` and may report incomplete results (exit `3`).
See [the complete CLI/JSON/exit contract](docs/CLI.md). The checkout must be
from an independently reviewed source revision before it is used for
production automation.

### Agent-guided, project-specific setup

Open the **target repository** in Codex or Claude Code, then give the agent
[the setup prompt](prompts/setup-project.md) and a reviewed agent-dotfiles
checkout/prefix. The prompt starts with read-only discovery, prefers native
tools, and changes only explicitly approved, non-colliding **environment**
integration files. PHP projects may benefit from the optional
[project-onboarding skill](docs/PROJECT_ONBOARDING.md); other projects may
need nothing. An existing agent-loop workflow stays owned and configured
by agent-loop. Do not create a second memory store, global startup hooks
or a duplicate workflow.

A fresh Codex/Claude host-side setup has **not yet been independently proven**
by these deterministic repository tests. Such verification remains a
separate review gate for this prompt.

### Optional shell activation

For an explicit, temporary Bash session, source the profile and remove it when
the task ends:

```sh
source /absolute/path/to/agent-dotfiles/.bashrc
agent_workspace --root /absolute/path/to/project
agent_search 'function save(' --root /absolute/path/to/project --glob '*.php'
agent_deactivate
```

Use `.zshrc` in Zsh. In a fresh non-interactive shell, start Bash with
`env -u BASH_ENV bash --noprofile --norc` or Zsh with `zsh -f`, then explicitly
source the reviewed profile. The [shell contract](docs/SHELL.md) describes the
namespaced helpers, exit statuses, and activation guarantees.

## Pick the smallest useful tool

| Question | Recommended path |
| --- | --- |
| You know the file and only need a quick answer | Native `rg`, `git`, or a source read |
| You need match coordinates and explicit completeness | `agent-dotfiles search` or `agent_search` |
| You need exact lines tied to a file identity | `agent-dotfiles read` or `agent_read` |
| You need the complete patch for one literal file | `agent-dotfiles git-patch` or `agent_patch` |
| You need a bounded checkout identity and current worktree state | `agent-dotfiles workspace` or `agent_workspace` |
| You need PHP symbols or callers | [agent-map](https://github.com/voku/agent-map) through the current agent-loop workflow |
| You need a capability/readiness report | `agent-dotfiles doctor --profile minimal` |

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
- Explicit `minimal`, `git`, `php`, and `shell` profiles. They are diagnostic
  declarations, not installers, plugin loaders, aliases, or automatic routing.
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

Start with the [documentation index](docs/README.md) or the
[full CLI reference](docs/CLI.md) for JSON schemas and exit codes. The public project paths
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
