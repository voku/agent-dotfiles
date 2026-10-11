# Documentation map

The root [README](../README.md) is the product entry point. This index keeps
setup and reference material separate from experiment history, so a first-time
user does not need to read every CI receipt before trying the tools.

## Start here

- [Getting started](../README.md): who this is for, a safe first run, and the
  smallest way to enable project-local agent skills
- [Agent-assisted project setup prompt](../prompts/setup-project.md): paste into
  Codex or Claude Code in the **target project** to discover and set up useful
  optional integrations
- [PHP project-onboarding skill](PROJECT_ONBOARDING.md): canonical source,
  explicit Codex/Claude projection, and guarded manual fallback
- [Installation, verification and rollback](INSTALLATION.md): pin source,
  preview contents, install to a private prefix and verify without altering HOME

## Reference and operational contracts

- [CLI commands and exit codes](CLI.md)
- [Bash/Zsh modules and activation](SHELL.md)
- [Git context helpers](GIT_CONTEXT.md)
- [Tool matrix](TOOL_MATRIX.md)
- [Context and completeness policy](CONTEXT_POLICY.md)
- [Security](SECURITY.md)
- [agent-loop integration boundary](AGENT_LOOP.md)

## Evaluation and implementation history

These documents record scoped experiments, historical source pins and
investigations. Do not treat their old status statements as today's release,
current HEAD or authorization to change the host.

- [Full-cycle baseline](FULL_CYCLE.md)
- [Controlled shell/CLI evaluation](EVALUATION_2026-10-11.md)
- [Real owner-capability experiments](MOMENTUM_EXPERIMENTS.md)
- [Governed PHP quality cycle](QUALITY_CYCLE_17.md)
- [Quality-first preflight](QUALITY_FIRST_PREFLIGHT.md)
- [Mutation testing](MUTATION_TESTING.md)
- [Shell refactor record](SHELL_REFACTOR.md)
- [Upstream inspiration and differences](../UPSTREAM.md)

## Repository areas

| Path | Ownership |
| --- | --- |
| `.bashrc`, `.zshrc`, `.shellrc`, `.functions`, `.exports` | Explicit shell entry points |
| `shell/core/`, `shell/modules/` | Reviewed runtime activation and namespaced functions |
| `bin/`, `agent_dotfiles/` | JSON CLI entry point and implementation |
| `skills/` | Portable, opt-in coding-agent skills |
| `prompts/` | Copyable human-to-agent setup instructions; **not** auto-executed |
| `tools/`, `install.sh` | Offline pinned installer and development tooling |
| `tests/`, `.github/workflows/` | Unit, integration and CI validation |
| `docs/` | Guides, operational contracts and historical evidence |

Runtime paths are intentionally stable because the installer pins their bytes
and manifests. Do not move them solely for cosmetic directory symmetry.
