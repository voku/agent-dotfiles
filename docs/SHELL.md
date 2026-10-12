# Agent-owned Bash and Zsh setup

These dotfiles share the familiar layout of `voku/dotfiles`, but their contents
are independently designed for agents. They do not source upstream/user profiles,
load `.redpill`, create terminal sessions, configure prompts or change shell options.
No helper shadows `git`, `rg`, `cd` or another native command.

## Explicit activation

Use a reviewed checkout for development or a verified, full-commit-pinned private
prefix for a fresh consumer. [Installation](INSTALLATION.md) explains verification.

```bash
# Bash
source /absolute/agent-dotfiles/.bashrc
# Zsh (use this instead in a Zsh shell)
source /absolute/agent-dotfiles/.zshrc
```

For hosts that run each tool call in a new shell, activate in that call explicitly:

```sh
env -u BASH_ENV bash --noprofile --norc -c '. "$1/.bashrc" || exit $?; shift; agent_search "$@"' \
  consumer /absolute/agent-dotfiles 'function save(' --root /project --glob '*.php'
```

Activation is silent on success. It exports `AGENT_DOTFILES_HOME` and defines only
the functions below. PATH, working directory, positional arguments and shell options
are preserved. Shared files are resolved beside the selected profile, never from
HOME or the project being investigated. Use `env -u BASH_ENV bash --noprofile --norc` or `zsh -f`
when creating a dedicated shell. Clearing `BASH_ENV` is required: Bash reads
that inherited startup file even with `--noprofile --norc`. Activation itself cannot undo an already-loaded
user configuration. Source `.bashrc` in Bash and `.zshrc` in Zsh, not via `sh`.

Activation refuses existing owned names or `AGENT_DOTFILES_HOME` rather than
replacing custom definitions. Run `agent_deactivate` before activating another
version. No eval-based restoration or command interception is involved.

## Explicit shell lifecycle and modules

`.bashrc` and `.zshrc` delegate to `.shellrc`, which resolves the reviewed
installation root and loads exactly `shell/core/activation.sh`. Core activation
checks the required assets, executable, exported namespace and owned function
names **before** exporting anything. `.functions` then loads the reviewed
`shell/modules/context.sh`, `shell/modules/git.sh` and
`shell/core/deactivation.sh` in fixed order. There is no plugin discovery,
host startup sourcing, dynamic evaluation or per-host runtime configuration.

The pinned installation manifest includes and hashes both lifecycle files,
all modules and each entry point. Earlier pre-core and pre-modular manifests
remain verifiable for rollback; new installs require the complete tree.

## Choose tools by the evidence needed

Use native `rg -n` and a source read when the file or symbol location is already
known. The profile is optional; do not repeat a successful native search simply
to use a helper. Use `agent_search` for structured match coordinates and explicit
completeness, `agent_read` for byte-exact ranges tied to a whole-file digest, and
`agent_patch` when a complete literal-file patch is the required evidence. PHP
symbols and callers still belong to agent-map and the Loop investigation skill.

Scope discovery before reducing its output limit:

```bash
agent_workspace --root /project
agent_search 'sha256' --root /project --path agent_dotfiles --glob '*.py'
agent_read agent_dotfiles/cli.py --root /project --start 220 --end 285
```

Keep activation failures and search statuses visible; a trailing successful
command must not replace the status of the evidence command. Check completeness
fields too. Exit 3 means the search is
incomplete: narrow its scope or retrieve the missing evidence before drawing a
conclusion. A short result that omits the implementation costs another search.
Loop lifecycle and Learning syntax must come from the pinned owner's help and
current structured next action; shell helpers do not replace those contracts.

## Helpers

All helpers preserve argument boundaries, stdout, stderr and exit status. The
context helpers produce exactly the standalone CLI's JSON, limits and errors.
Use `--help` on a helper for the corresponding CLI contract.

| Helper | Operation |
| --- | --- |
| `agent_dotfiles` | Invoke any standalone CLI subcommand |
| `agent_doctor` | Actual executable capability inventory |
| `agent_workspace` | Bounded Git checkout identity and worktree status |
| `agent_files` | Ignore-aware file discovery |
| `agent_search` | Literal search by default; explicit regex/glob/path options |
| `agent_read` | Exact source ranges and whole-file hash |
| `agent_tracked` | NUL-safe tracked inventory |
| `agent_status` | Individual worktree paths, including untracked files |
| `agent_patch` | Complete patch for one literal tracked file |
| `agent_history` | Native Git log, with literal pathspecs and no pager/color |
| `agent_blame` | Native Git line-porcelain blame, with literal pathspecs |
| `agent_deactivate` | Remove this namespace and installation-location export |

```bash
agent_files --root /project --hidden --limit 100
agent_workspace --root /project
agent_search 'invoice.total' --root /project --path templates --glob '*.twig'
agent_read 'src/name [v2].php' --root /project --start 20 --end 70
agent_tracked --root /project
agent_status --root /project
agent_patch 'src/name [v2].php' --root /project
(cd /project && agent_history -- src/Service.php)
(cd /project && agent_blame -- src/Service.php)
```

Native history/blame use Git's own syntax and output, not JSON envelopes or the
CLI's output caps. History/blame operate in the current repository; their arguments are passed to
`git log` and `git blame`, respectively. Use a subshell as above for another root.
Read the complete patch or source when required; bounded discovery never proves
that omitted context is irrelevant. Exit 3 signals incomplete discovery, exit 1
means a completed search found no matches, and exit 2 means a CLI error.
Untracked/ignored files need explicit `agent_read` evidence; they cannot supply
tracked patch evidence. Structural PHP questions remain owned by agent-map and
agent-loop's investigation workflow.

## Verify the citation as well as the content

Record the worktree or exact Git commit that produced a source finding. Use the
original path and source positions, not line numbers from a JSON display or a
different revision. A structured read does not prevent a manually misquoted
citation: verify the cited declaration or statement in that exact source before
recording the conclusion. Keep independent review in the governed workflow.

## Rollback

Run `agent_deactivate` or exit the dedicated shell. Activate the previous verified
prefix in the next fresh consumer; never replace a running session's toolset.
The installer never modifies HOME startup files, so uninstall needs no global
configuration restoration. Optional tools cannot prevent agent-loop from starting.
