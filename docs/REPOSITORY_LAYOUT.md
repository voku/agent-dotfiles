# Repository layout and file ownership

This is an **agent environment**, not a general-purpose dotfile manager. The checkout contains three distinct kinds of file. No path is copied to `$HOME` by the supported installer.

| Owner | Source paths | Consumer behavior |
| --- | --- | --- |
| Optional shell environment | `.bashrc`, `.zshrc`, `.shellrc`, `.exports`, `.functions`, `shell/core/`, `shell/modules/` | Explicitly sourced from an approved checkout or pinned private prefix; never inserted into user startup |
| Optional CLI and diagnostics | `bin/agent-dotfiles`, `agent_dotfiles/`, `profiles/*.json` | Pinned private-prefix payload; profiles are read-only tool-capability declarations, **not shell configuration** |
| Optional curated skills | `skills/project-onboarding/`, selected portable `skills/`, `skills/portable-skills.json` | Pinned payload; portable skill content is owned upstream and is never silently installed into a host |
| Repository-only build/test tools | `tools/`, `tests/`, `.github/`, `mutation.toml`, `requirements-mutation.txt` | Used to develop and validate this repository; not consumer dotfiles |
| Examples and maintenance documentation | `examples/gitconfig.agent.example`, `docs/`, `README.md`, `AGENTS.md` | Source references only; the Git alias example is **not** installed or activated |
| Reviewed project knowledge | `MEMORY.md`, `docs/decisions/`, `.agent-loop/init.json`, selected `.agent-loop/learning/` records | Versioned in this repository, not copied to a consumer's home |

## The currently confusing names

- `.exports` is a shell activation input today. It **only** exports the reviewed `AGENT_DOTFILES_HOME`. It is not an LLM configuration bundle.
- `.functions` is a fixed loader for the namespaced, machine-readable helper functions.
- `profiles/` describes the required/optional executable inventory for `doctor` and `firstInstall.sh plan`; selecting a profile does **not** activate, install, or tune anything.
- `examples/` contains a per-invocation Git alias *example*, not another runtime profile or configuration layer.

Keep `profiles/` for diagnostics only if it demonstrably solves a distinct problem. The former `config/` entry is now an `examples/` entry. This changes the path of an **uninstalled example** only, so users invoking it by absolute path must update that path; no runtime payload or default configuration changes.

## Direction, not an unverified migration

A future physical layout may group shipped payload under a single `dotfiles/` or `runtime/` root and place maintainer utilities under `dev/`. Do **not** copy/move runtime entrypoints merely to make the tree attractive: they are referenced by pinned installer allowlists, import paths, actual Bash/Zsh source semantics, shell tests and CI. First freeze a cold-install path manifest, move one owner at a time, compare the old/new installed payload by path and SHA-256, and require tests for both fresh and previously installed consumers.

Agent-specific defaults belong in **reviewed, opt-in, namespaced** shell behavior or narrow per-command Git options. Do not globally set `PAGER`, `GIT_PAGER`, `NO_COLOR`, `GIT_OPTIONAL_LOCKS` or replace common native commands merely to claim fewer output bytes. Preserve full patches, errors and truncation evidence.

## Project-local workflow knowledge

`agent-loop` governs approved tasks, decisions, validation and Learning. This repo owns only its *own* versioned project knowledge:

- `MEMORY.md` indexes durable, reviewed rules with executable sources.
- `docs/decisions/` contains architectural decisions and tradeoffs.
- `.agent-loop/init.json` and `.agent-loop/learning/config.json` select a project-local Learning root, following the upstream shape.
- Only independently reviewed findings in `.agent-loop/learning/findings/validated/*.json` are eligible for Git. Raw task/session data and derived caches are excluded by `.gitignore`.

These files establish a **storage convention**, not proof that an agent-loop run has completed or automatically promoted learning. Follow the installed agent-loop version's actual `enter` / `workflow` / `learning` contracts. Do not fabricate approvals, completed sessions, findings or useful outcomes.

## Product acceptance gate

The historical [governed comparison](EVALUATION_2026-10-11.md) and [full-cycle record](FULL_CYCLE.md) do not prove general improvement. [Evaluation issue #12](https://github.com/voku/agent-dotfiles/issues/12) remains the owner of a new, reproducible comparison: native baseline vs pinned CLI vs explicitly sourced shell, identical task seeds/model/settings/agent-loop revision, independent held-out correctness, full source evidence, usage receipts, actual elapsed time and provider token telemetry where available. Source and sink of each metric must be recorded. Failing to record tokens is **unknown**, not a token saving.

**Adoption rule:** correctness and complete evidence first. Require a reproducible improvement in real completed agent tasks before adding default aliases, installing more dependencies or recommending automatic routing.
