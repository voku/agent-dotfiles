# Project onboarding skill

`project-onboarding` is a small, opt-in skill for starting a PHP maintenance
task with verified project facts instead of a guessed test command. It discovers
the current Git state, exact Composer metadata and declared scripts, available
verification configuration, supplied failure evidence, and the smallest
relevant source location. It does not run project tests, install dependencies,
edit files, or replace agent-loop and agent-map ownership.

The canonical source is one file:

```text
skills/project-onboarding/SKILL.md
```

It is included in every new, full-commit-pinned private-prefix installation and
therefore covered by `install.sh plan`, `verify`, and safe refusal on modification.
Older installations remain valid but do not contain this optional skill.

## Project-local Codex and Claude Code projection

Review the installed skill first. Then, from the target project, use an existing
agent-loop installation to project the identical source into the coding host's
project-local skill directory:

```sh
vendor/bin/agent-loop init sync-skills --agent=codex \
  --skills-root=/absolute/approved-agent-dotfiles-prefix/skills
vendor/bin/agent-loop init sync-skills --agent=claude \
  --skills-root=/absolute/approved-agent-dotfiles-prefix/skills
```

The first command targets `.codex/skills/project-onboarding/SKILL.md`; the
second targets `.claude/skills/project-onboarding/SKILL.md`. `agent-loop` owns
that projection, including its managed-asset manifest and conflict handling.
Run the command only for the host you want to use. Start a fresh agent session
after projection; an already-running host need not rediscover a new skill.

If agent-loop is unavailable, copy the reviewed source manually only into an
empty project-local target. This is an explicit fallback, not a bootstrap
requirement:

```sh
skill_source=/absolute/approved-agent-dotfiles-prefix/skills/project-onboarding
skill_target=/absolute/project/.codex/skills/project-onboarding
test ! -e "$skill_target" || { printf '%s\n' 'refusing to replace an existing skill' >&2; exit 2; }
mkdir -p "${skill_target%/*}"
cp -R "$skill_source" "$skill_target"
cmp -s "$skill_source/SKILL.md" "$skill_target/SKILL.md"
```

For Claude Code, replace `.codex` with `.claude`. To roll back a manual copy,
first compare `SKILL.md` with the approved source; remove only that matching
`project-onboarding` directory. Do not overwrite a local skill or set global
`CODEX_HOME`, `CLAUDE_SKILLS_DIR`, shell startup files, PATH, hooks, or Git
configuration.

## What the skill proves

The skill has a real-PHP contract against pinned `voku/agent-loop` source:
its Composer scripts/configuration and an exact source range are recorded in
the machine-readable preflight artifact. That validates installation and
discovery compatibility. It does not measure a live model's effectiveness;
model tokens, repeated retrieval, correctness, and elapsed time must be
captured in a separate fresh-consumer evaluation.
