# Git evidence without lossy shortcuts

The original [`voku/dotfiles/.gitconfig`](https://github.com/voku/dotfiles/blob/master/.gitconfig)
includes extensive interactive Git aliases. The companion
[`config/gitconfig.agent.example`](../config/gitconfig.agent.example) keeps
**only read-only Git subcommands** and never overrides built-in Git commands.
No aliases are installed by default.

To use one alias for a single invocation (without changing `~/.gitconfig`):

```sh
git -c include.path="$PWD/config/gitconfig.agent.example" agent-history -n 10
git -c include.path="$PWD/config/gitconfig.agent.example" agent-files
```

The NUL-delimited aliases require a NUL-aware consumer (not `grep`/`cut` on
lines). `agent-history` returns hash, ISO timestamp and subject, not the full
commit message; use `git show -s --format=fuller HASH` for full metadata.

### Recommended direct Git commands

```sh
# Git index vs filesystem: these are not interchangeable.
git ls-files -z
rg --files -0

# Identify changes without losing paths that contain spaces/newlines.
git status --porcelain=v1 -z --untracked-files=all
git diff --name-status -z -M
git diff --cached --name-status -z -M

# Fetch complete patches after candidate selection, never a silent diffstat.
git --no-pager diff --no-ext-diff --no-textconv --binary --full-index -- path/to/file.php
git --no-pager diff --cached --no-ext-diff --no-textconv --binary --full-index -- path/to/file.php

# Find commits introducing/removing a literal string (pickaxe, not all occurrences).
git log -S'oldBehavior' --all --format=fuller -- path/to/file.php

# Regex-based historical changes and rename-aware history (one file).
git log -G'regexp' --all -- path/to/file.php
git log --follow --format=fuller -- path/to/file.php

# Full attribution for a specific source range.
git --no-pager blame --line-porcelain -L 25,65 -- path/to/file.php
```

Search-history scope matters: `git log -S` finds changes in occurrence counts,
not a guaranteed complete semantic origin. `--follow` only follows one file and
may not capture complex histories. Cross-repo and code-generated origins remain
separate investigative questions.

### Tool selection

Use the new `agent-dotfiles tracked` for safely decoded tracked names and
`agent-dotfiles git-patch path/to/file.php` for an exact, SHA-bound file patch.
Neither substitutes the necessary project-wide diff during review. For PHP
symbol ownership/callers/impact, a current `agent-loop map` is still the
preferred structural source; Git history helps explain *when*, not *what is
true now*.
