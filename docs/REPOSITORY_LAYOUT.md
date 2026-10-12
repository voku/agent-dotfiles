# Repository layout and file ownership

This is an **agent environment**, not a general-purpose dotfile manager. The checkout contains three distinct kinds of file. No path is copied to `$HOME` by the supported installer.

| Owner | Source paths | Consumer behavior |
| --- | --- | --- |
| Optional shell environment | `.bashrc`, `.zshrc`, `.shellrc`, `.exports`, `.functions`, `.aliases`, `.redpill/` | Explicitly sourced from an approved checkout or pinned private prefix; never inserted into user startup |
| Optional CLI and diagnostics | `bin/agent-dotfiles`, `agent_dotfiles/`, `profiles/*.json` | Pinned private-prefix payload; profiles are read-only tool-capability declarations, **not shell configuration** |
| Optional curated skills | `skills/project-onboarding/`, selected portable `skills/`, `skills/portable-skills.json` | Pinned payload; portable skill content is owned upstream and is never silently installed into a host |
| Repository-only build/test tools | `tools/`, `tests/`, `.github/`, `mutation.toml`, `requirements-mutation.txt` | Used to develop and validate this repository; not consumer dotfiles |
| Examples and maintenance documentation | `examples/gitconfig.agent.example`, `docs/`, `README.md`, `AGENTS.md` | Source references only; the Git alias example is **not** installed or activated |
| Agent-loop project knowledge | `MEMORY.md`, `docs/decisions/` | Versioned maintainer knowledge for this repository; excluded from every consumer installation |

## The currently confusing names

- `.exports` is a shell activation input today. It **only** exports the reviewed `AGENT_DOTFILES_HOME`. It is not an LLM configuration bundle.
- `.functions` is a fixed loader for the namespaced, machine-readable helper functions.
- `.aliases` keeps a familiar dotfile name but intentionally exposes named
  functions: ordinary aliases are not a reliable non-interactive agent interface.
- `.redpill/` is the one reviewed runtime tree, not a plugin manager, profile
  catalog or local-override directory.
- `profiles/` describes the required/optional executable inventory for `doctor`;
  it is the sole checked-in diagnostic catalog. `firstInstall.sh plan` has
  fixed planner selections in code for package recommendations, not a second
  data/configuration tree. Neither selection activates, installs or tunes
  anything.
- `examples/` contains a per-invocation Git alias *example*, not another runtime profile or configuration layer.

Keep `profiles/` for diagnostics only if it demonstrably solves a distinct problem. The former `config/` entry is now an `examples/` entry. This changes the path of an **uninstalled example** only, so users invoking it by absolute path must update that path; no runtime payload or default configuration changes.

## Runtime move completed deliberately

The shipped shell implementation now has one physical root: `.redpill/`. Root
entry points remain familiar and small because they are the stable explicit
activation surface. The pinned installer allowlist, shell activation tests,
fresh-install test and legacy-manifest checks moved together. Future layout work
must keep that same discipline: change one owner at a time, compare the pinned
payload by path and SHA-256, and test both fresh and previously installed
consumers.

Agent-specific defaults belong in **reviewed, opt-in, namespaced** shell behavior or narrow per-command Git options. Do not globally set `PAGER`, `GIT_PAGER`, `NO_COLOR`, `GIT_OPTIONAL_LOCKS` or replace common native commands merely to claim fewer output bytes. Preserve full patches, errors and truncation evidence.

## External workflow owner: agent-loop

`agent-dotfiles` distributes **optional tools, an explicit shell environment,
and a pinned set of opt-in skill files**. This package owns the
`project-onboarding` skill; curated portable skills remain sourced and maintained
by `voku/agent-skills` and are distributed without silently activating them.
Package contents and content ownership are separate from agent-loop governance.
It does not ship `agent-loop`, a Loop project scaffold, `.agent-loop/` state,
`MEMORY.md`, a Recall manifest, Learning records or rules for promoting findings.
A host may use this environment to execute a *separately installed and pinned*
`agent-loop`; Loop remains responsible for tasks, sessions, approvals, review,
Learning, Recall and persisted project memory in the **consumer's actual project**.
Its configuration and owner workflow are not copied into a consumer by the
dotfiles installer. Consult the
[documented integration boundary](AGENT_LOOP.md).

Repository maintainers may independently adopt agent-loop for development
work. This checkout keeps its short reviewed `MEMORY.md` and decisions in Git
for that owner, while ignoring raw `.agent-loop/` execution state. Neither is a
feature or default installation behavior of the consumer product.

## Product acceptance gate

The historical [governed comparison](EVALUATION_2026-10-11.md) and [full-cycle record](FULL_CYCLE.md) do not prove general improvement. They cannot be used to infer a steady-state time disadvantage when their timing mixes setup, orchestration or provider delays. The [steady-state protocol](STEADY_STATE_EVALUATION.md) explicitly separates one-time installation and per-project onboarding from repeated agent tasks. [Evaluation issue #12](https://github.com/voku/agent-dotfiles/issues/12) remains the owner of a new, reproducible comparison: native baseline vs pinned CLI vs explicitly sourced shell, identical task seeds/model/settings/agent-loop revision, independent held-out correctness, full source evidence, usage receipts, actual elapsed time and provider token telemetry where available. Source and sink of each metric must be recorded. Failing to record tokens is **unknown**, not a token saving.

**Adoption rule:** correctness and complete evidence first. Require a reproducible improvement in real completed agent tasks before adding default aliases, installing more dependencies or recommending automatic routing.
