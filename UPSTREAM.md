# Upstream provenance

This repository is an independent, reduced-scope rewrite informed by:

- https://github.com/voku/dotfiles (original shell and .redpill environment)
- https://github.com/voku/dotfiles/issues/48 (research: agent-safe CLI profile)
- https://github.com/voku/agent-loop/issues/756 (evidence-driven agent CLI integration)

The existing dotfiles load interactive shell aliases, plugins, prompt customizations and history hooks. Those are useful for humans but not stable machine interfaces. In particular, `.redpill/plugins/available/fzf.plugin.bash` defines `fd()` as a directory-changing function, which can shadow the separate `fd` file-search binary in an interactive shell. This project invokes binaries directly and chooses `fdfind` when `fd` is unavailable.

No upstream source files, binaries, fonts, themes or historical git metadata were imported into this project. Its implementation is new and intentionally narrow. A GitHub fork in the same owner account is unsupported; an independent repository is the appropriate release destination.
