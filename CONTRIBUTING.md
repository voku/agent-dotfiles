# Contributing

This project prepares a coding-agent shell environment. Git, rg, shell and the
project's own tools are its user interface; avoid adding another command
wrapper without evidence from real coding sessions.

Keep changes focused, preserve complete errors and source context, and never
edit user startup files or global Git configuration. Agent-loop owns task
workflow; agent-map owns structural code mapping; agent-skills owns portable
guidance.

The installer uses Python internally for pinned commit reads and manifest
verification. It is not an agent-facing runtime. Validate shell setup changes
in a disposable Debian/Ubuntu machine and a fresh Bash/Zsh session. The current
working tree intentionally has no CLI contract suite; real coding-session
dogfooding is the next product validation step.

Report vulnerabilities privately as described in [docs/SECURITY.md](docs/SECURITY.md).
For general questions and reproducible bugs, use [SUPPORT.md](SUPPORT.md).
