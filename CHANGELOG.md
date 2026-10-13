# Changelog

## 0.6.0

- Become shell-only: remove the Python CLI, `tools/`, installer, first-install
  planner, capability profiles and vendored skills ([ADR 0003](docs/decisions/0003-shell-only.md)).
- Move `agent_git`/`agent_rg` from `.aliases` into `.functions`; drop `.aliases`.
- Add `.redpill/config/agent.env`: per-tool variables that remove progress bars,
  color, pagers, update nags and prompts (Git, Composer, npm, pip, Cargo, ...),
  applied only when unset and removed exactly by `agent_deactivate`.
- Add helpers `agent_curl`, `agent_require` (capability check), `agent_head`
  (truncation that is always announced), `agent_usage`, `agent_os`, `agent_ports`,
  `agent_free_port`, `agent_json`, `agent_codepoints`, `agent_php_lint` and `agent_extract`.
- Keep #61's `agent_context`, `agent_root`, `agent_diff`, `agent_diff_check` and
  `agent_mkcd`, now in `.functions` with tests; drop its installer, `activate.sh`
  and `git-env.sh` (see ADR 0003).
- Derive the owned function namespace from `.functions` instead of two hand-kept lists.
- Replace `.redpill/core` and `.redpill/modules` with `.redpill/lib` and `.redpill/config`.
- Move `project-onboarding` to `voku/agent-skills`.

## 0.5.0

- Establish one reviewed `.redpill/` Bash/Zsh runtime with explicit, reversible
  activation and per-invocation `agent_git`/`agent_rg` defaults; retain verification
  and removal of older pinned installation manifests.
- Add read-only first-install capability plans, diagnostic tool profiles and
  trustworthy Git workspace evidence without provisioning host packages.
- Distribute the project-onboarding skill and a pinned selection of portable
  agent-skills; keep workflow, Learning, Recall and memory with agent-loop.
- Document the complete pinned install/verify/activate/deactivate/uninstall path
  and prove byte-identical manifests and equivalent behavior across two consumers,
  with unchanged HOME, project and source trees.
- Make the workflow test fixture portable to Python3-only hosts and provision
  real ripgrep in CI so search-reliability measurements execute rather than skip.
- Measure exact-search correctness under four fixed host configurations: native
  `rg` 1/4, `agent_rg` 4/4, explicit native `rg --no-config` 4/4. This is a narrow
  configuration-isolation result; general productivity, speed and token benefits
  remain inconclusive.

## 0.4.0

- Require Linux Bash/Zsh activation tests and ShellCheck validation of the root
  shell layout; preserve source paths and caller shell state.
- Add cross-range whole-source digest and LF-only source-coordinate regression
  coverage, plus evidence-driven native/structured tool selection guidance.
- Preserve activation failures in documented fresh-shell invocations; require
  exact-revision citations and actual approved-scope checks before mutation.
- Record independently graded three-way maintenance, held-out oracles and
  workflow setup/scope failures without claiming general productivity or token savings.
- Reject abbreviated installer flags that could override the root source owner;
  verify the exact candidate installation lifecycle in isolated Bash/Zsh CI.

- Add explicit agent-owned Bash/Zsh profiles, shared exports and namespaced
  context helpers without changing user startup files, PATH or shell options.
- Add root `install.sh` for pinned private installation, verification and removal;
  include the shell assets in the verified installation manifest.
- Remove generated release and benchmark payloads from the working tree;
  preserve immutable historical evidence links.

## 0.3.0

- Integrate targeted mutation testing with summaries retained on nonzero reports.
- Preserve literal file-scoped patches, subdirectory roots and bounded index checks.
- Expose individual untracked files in Git status.
- Add explicit offline, full-commit-pinned installation, verification and safe removal.
- Reject nonexistent noninitial ranges in empty files, found independently by
  fresh governed consumers; preserve initial empty-file reads.
- Document optional consumer activation, rollback, coordinate frames and measured
  comparison limits. No agent-loop host policy or global shell configuration changes.


## 0.2.0 - Context-first navigation

- Added exact, source-digest-bound `read` and full-fidelity `git-patch` commands.
- Added NUL-safe Git tracked-files inventory (`tracked`).
- Added scoped search via `--path`/`--glob`; removed `rg --max-columns-preview` to avoid silent line loss.
- Prevented user ripgrep configuration from changing wrapper semantics.
- Added opt-in, project-scoped read-only Git aliases and evidence-first/context policy documentation.
- Expanded optional tool discovery (`ast-grep`, `ctags`, `difft`, `delta`); no automatic installation or hook interception.
- Added security, context, unusual-filename, rename and real-Git integration tests.


## 0.1.0 - Initial bootstrap

- Added non-interactive, read-only `doctor`, `files`, `search` and `git-status`.
- Added bounded, machine-readable JSON output and explicit truncation status.
- Added optional `fd`/`fdfind` detection without using the interactive shell.
- Added first-party executable contract tests and CI matrix.
- Documented upstream dotfiles provenance and separation from `agent-loop`.

At the original bootstrap checkpoint, no release tag or GitHub repository had been published.

## Earlier bootstrap notes

- Import the v0.2.0 candidate with original GitHub LICENSE preserved.
- Add pinned Bashunit integration tests for source fidelity, Git evidence and executable status codes, alongside the existing Python contracts.
- Remove obsolete repository-creation helper now that voku/agent-dotfiles exists.
