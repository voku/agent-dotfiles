# Maintainer memory

- Product: an optional native-first shell environment and reviewed agent skills.
  The host's Git, rg, shell and project tools are the agent interface.
- Consumer runtime: explicit Bash/Zsh profiles, session-only Git defaults, and
  opt-in skills. No command wrappers, prompt framework, user startup edits or
  global Git changes.
- Installer: pinned private-prefix copy and manifest verification. Its Python
  code is internal plumbing; do not restore a Python agent CLI without evidence
  from real coding sessions.
- Workflow owner: separately installed agent-loop owns task lifecycle, review,
  Learning, Recall and persisted project memory.
- Evaluation: setup correctness is not productivity evidence. Use real coding
  tasks and complete source/error context to decide what adaptations help.
