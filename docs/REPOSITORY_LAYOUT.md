# Repository layout

The consumer payload is an explicitly activated shell environment and a
reviewed set of opt-in skills. There is no agent-specific executable or
diagnostic profile catalog.

| Purpose | Paths |
| --- | --- |
| Shell environment | `.bashrc`, `.zshrc`, `.shellrc`, `.exports`, `.functions`, `.aliases`, `.redpill/` |
| Shared session entry and Git defaults | `activate.sh`, `git-env.sh`, `.gitconfig` |
| Host setup and pinned installer | `bootstrap.sh`, `firstInstall.sh`, `install.sh`, `tools/` |
| Agent guidance | `skills/`, `skills/portable-skills.json` |
| Maintainer knowledge | `MEMORY.md`, `docs/decisions/` |

No file is copied into `$HOME` or a shell startup file. The shared session is
activated by sourcing `activate.sh` in the current shell. `.aliases` contains a
small set of optional repo-orientation and navigation functions; native `git`,
`rg`, shell and project commands remain fully available.

The Python pinned installer is internal maintenance code. Its allowlist copies
only reviewed runtime and skill files, validates a full source commit, and
writes a manifest used for verify and uninstall. Installer code, docs and
maintainer memory are not part of the consumer payload.

## Workflow ownership

This repository does not ship agent-loop, task policy, `.agent-loop/` state or
consumer memory. A separately installed agent-loop owns planning, sessions,
approvals, review, Learning, Recall and persisted memory. Portable skill content
remains attributed to its upstream repository and is opt-in.
