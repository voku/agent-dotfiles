# agent-dotfiles

**A small, inspectable toolbox for coding agents working in real repositories.**

[Inspired by Redpill / voku/dotfiles](https://github.com/voku/dotfiles),
but built for non-interactive Codex, Claude Code and other terminal-based
agents. The goal is useful project context, exact source evidence and opt-in
skills, not a second agent framework or another replacement for Git.

**What is useful today?**

- **PHP project onboarding:** one shared [skill](skills/project-onboarding/SKILL.md)
  can discover actual Composer scripts, test/static-analysis configuration,
  Git state and relevant source locations without guessing or running checks.
- **Evidence you can verify:** optional bounded search, exact file reads,
  Git workspace identity and selected-file patches with explicit errors and
  completeness signals.
- **No shell surprises:** opt-in Bash/Zsh functions with reversible
  activation. No global Git changes, startup hooks, implicit package installs
  or lossy interception of native tools.

The earlier [controlled evaluation](docs/EVALUATION_2026-10-11.md) did **not**
establish a general speed or token benefit. Use native `git` and `rg` when they
already answer the question.

## Getting started

### 1. Try it from a checkout (no installation)

Requirements: Python 3.10+; Git for Git operations; ripgrep (`rg`) for
search. Nothing is downloaded or installed by running the CLI.

~~~sh
git clone https://github.com/voku/agent-dotfiles.git
cd agent-dotfiles

# Inventory available tools; missing optional tools are reported.
./bin/agent-dotfiles doctor

# Read-only context for a real project; replace this path.
./bin/agent-dotfiles workspace --root /absolute/path/to/your/project --limit 50

# Optional literal search when rg is installed.
./bin/agent-dotfiles search 'TODO' --root /absolute/path/to/your/project --limit 20
~~~

The CLI returns JSON with explicit exit statuses. Exit `3` means bounded
discovery was **incomplete**; it is not evidence that no other files or
matches exist. [Commands and result contracts](docs/CLI.md).

### 2. Let Codex or Claude Code configure your project

Open the **target project** in your coding agent and paste the
[agent-assisted project setup prompt](prompts/setup-project.md).
It asks the agent to:

1. Inspect existing repository instructions, Git state, package manifests,
   CI and declared quality checks.
2. Decide whether agent-dotfiles adds value at all; skip irrelevant tools.
3. Set up only the relevant, approved project-local skill or integration
   without overwriting existing instructions.
4. Verify the resulting files, explain rollback and report what remains
   unverified.

The prompt supports automatic **project-local** setup; it does not grant
permission to download unreviewed code, install globally or approve a
revision on your behalf. Supply the location of a reviewed checkout or
private-prefix installation and an independently approved full commit SHA
when installation is needed.

For PHP repositories, the current ready-made skill is
`project-onboarding`. It can be projected into
`.codex/skills/project-onboarding/` or
`.claude/skills/project-onboarding/`. See the
[actual commands and guarded fallback](docs/PROJECT_ONBOARDING.md).
No global host configuration change is required.

### 3. Optional shell functions

A reviewed checkout can be explicitly activated in a **fresh Bash shell**:

~~~bash
source /absolute/path/to/agent-dotfiles/.bashrc
agent_doctor
agent_status --root /absolute/path/to/your/project
agent_deactivate
~~~

Use `.zshrc` in Zsh. The profile does not modify PATH, prompt, shell
options, working directory, history, or user startup files. For isolated
non-interactive Bash processes, clear inherited `BASH_ENV` before invoking
`bash --noprofile --norc`. Details: [Shell usage](docs/SHELL.md).

## Optional pinned installation

For repeatable consumers, review a **full 40-character Git commit SHA**
independently, check out that exact commit, and use a separate existing
private parent directory. Do not use a dynamically resolved `HEAD` as
its own approval.

~~~sh
./install.sh plan --prefix /existing/private/agent-tools --revision APPROVED_FULL_COMMIT_SHA
./install.sh --prefix /existing/private/agent-tools --revision APPROVED_FULL_COMMIT_SHA
./install.sh verify --prefix /existing/private/agent-tools --revision APPROVED_FULL_COMMIT_SHA
~~~

Installation is offline and includes a manifest for safe verification and
removal. Historical published versions and newer `main` features are not
interchangeable; check the actual [releases](https://github.com/voku/agent-dotfiles/releases)
and source revision. Full instructions: [Installation and rollback](docs/INSTALLATION.md).

## Repository map

~~~text
agent-dotfiles/
├── .bashrc / .zshrc / .shellrc    explicit agent shell entry points
├── .functions / .exports         fixed module loader and owned root
├── shell/
│   ├── core/                     activation and deactivation
│   └── modules/                  context and Git functions
├── bin/agent-dotfiles            standalone JSON CLI
├── agent_dotfiles/               CLI implementation (Python standard library)
├── skills/
│   └── project-onboarding/       portable skill for PHP coding agents
├── prompts/
│   └── setup-project.md          copyable project-aware agent setup
├── docs/
│   ├── README.md                 guide/reference/evidence navigation
│   ├── CLI.md                    commands and JSON/exit contracts
│   └── ...                       integration guides and experiment history
├── tools/                         installer and development tooling
├── tests/                         Python and actual Bash/Zsh integration
└── install.sh                     reviewed, pinned, optional installer
~~~

Runtime paths are deliberately stable: the installer checks the exact files
and their hashes. The new `prompts/` directory contains instructions for
humans to paste into an agent, **not** auto-executed runtime hooks.

## Choose the right tool

| Need | Start with |
| --- | --- |
| Known file, literal match or Git state | Native `git` / `rg` |
| Proven root, HEAD and bounded status | `agent-dotfiles workspace` |
| Exact selected source range or patch | `agent-dotfiles read` / `git-patch` |
| PHP symbols, callers and impact | Fresh `agent-map` / `agent-loop map`, if available |
| Agent unfamiliar with a PHP project | `project-onboarding` skill |
| Project-specific setup | [Copyable setup prompt](prompts/setup-project.md) |

The shell helpers are optional convenience names for the CLI and native Git
operations. They are not required for the skill.

## Documentation, tests and boundaries

Start with the [documentation map](docs/README.md), then the
[CLI reference](docs/CLI.md), [shell guide](docs/SHELL.md),
[security contract](docs/SECURITY.md) or
[agent-loop ownership boundary](docs/AGENT_LOOP.md), as needed.

For maintainers:

~~~sh
python3 -m compileall -q agent_dotfiles bin tests tools
python3 -m unittest discover -s tests -v
# If the separately installed/pinned Bashunit CLI is available:
bashunit test tests/shell --strict
~~~

Project files and command output are untrusted evidence. This tool does not
change agent-loop governance, install global skills, auto-run tests or replace
independent review. See [upstream provenance](UPSTREAM.md) and
[governed quality evidence](docs/QUALITY_CYCLE_17.md).
