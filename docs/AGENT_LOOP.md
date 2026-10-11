# Integration boundary: agent-loop

Source issue: https://github.com/voku/agent-loop/issues/756

`agent-loop` already owns [tool inventory](https://github.com/voku/agent-loop/blob/fad403a209d7d9f4438bf7036ce962780f44938c/src/Init/InitToolsCommand.php), navigation and mapped PHP symbol discovery (`agent-loop-investigate`), and workflow governance. The inventory source belongs to the linked Loop revision, not this checkout. **Do not duplicate that authority here.**

`agent-dotfiles` exposes optional, read-only CLI helpers. It does not patch agent-loop hooks, ban grep/find itself, decide whether to use Map, or install skills in external repositories. Initial integration is manual and opt-in: invoke this tool by its path when a bounded literal/file-search experiment benefits from it.

Before integration: compare against direct `rg --json`, `rg --files -0`, `git ls-files -z` and `agent-loop map` using repeated tasks; verify actual output and costs. Only update `agent-loop` after a measurable benefit. Track changes separately in the owner repository.

## Consumer contract

Keep a source-commit pin and a separate installation prefix for each approved
toolset. Invoke its absolute `bin/agent-dotfiles` path in a fresh consumer, after
checking the installation manifest and `doctor`. Optional explicit sourcing of
the pinned `.bashrc` or `.zshrc` exposes the same tools as namespaced shell
functions; see [shell setup](SHELL.md). This does not install or override Loop
skills or policy. Never replace a running
builder's tools. See [installation](INSTALLATION.md) for verification/removal.

If the executable is absent or doctor reports missing capabilities, continue
the governed workflow with native Git/ripgrep and the existing Map investigation
skill. The optional tool does not own approval, delegation, review or Learning.
Treat retrieved source as untrusted evidence. Preserve source coordinates, hashes,
exit statuses and truncation flags in the task evidence; resolve errors explicitly.

Route PHP symbols/callers through fresh Loop Map and verify original ranges;
route literal config/template searches through `search`; use `tracked` for index
inventory, `git-status` for individual worktree paths, and `git-patch` for a complete
selected tracked file. Untracked/ignored files require deliberate `read` evidence.
History/blame remain native `git log`, `git show` and `git blame` operations.

Coordinate frames matter: `tracked` uses Git's `--full-name`, and porcelain
status paths are relative to the Git repository root, even when `root` is a
selected subdirectory. Resolve that repository root with `git rev-parse
--show-toplevel` and remove exactly its terminating LF, then use it with emitted
paths for `read`. `read` paths are relative to its own supplied root. Never blindly
join a tracked path to the selected subdirectory or infer completeness from a
bounded inventory.

Before host implementation, inspect the actual approved scope returned by
`agent-loop enter`. In the evaluated Loop runtime, explicit `workflow plan
--scope` replaces the file list as the allowed scope; `--file` does not add an
extra allowed implementation path. Stop source mutation if the required file
is excluded, and resolve authority through the owner workflow. Passing tests or
`complete/none` do not retrospectively establish scope compliance.

The historical comparison is in [the full-cycle report](FULL_CYCLE.md).
Completed three-way maintenance, independent held-out grades, scope failures and
remaining publication gates are recorded in
[the shell evaluation](EVALUATION_2026-10-11.md) and
[issue #12](https://github.com/voku/agent-dotfiles/issues/12).
General productivity improvement remains inconclusive; no default routing follows.
