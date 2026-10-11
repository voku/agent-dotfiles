# Selected portable skills

`agent-dotfiles` keeps its product-specific `project-onboarding` skill beside a
small, reviewed selection from [`voku/agent-skills`](https://github.com/voku/agent-skills).
The selection gives a fresh coding agent useful engineering guidance without
making the whole catalog, a package manager, or a global host directory a
runtime dependency.

The installed selection is recorded in `skills/portable-skills.json` with the
exact `agent-skills` commit and SHA-256 digest of every copied file:

- `coding-simplicity` for a smallest-correct-change check;
- `testing-best-practices` for meaningful regression evidence;
- `php-static-analysis` for PHP typing and analyzer work; and
- `language-onboarding-authoring` for creating an equally bounded onboarding
  skill for another language or ecosystem.

These are copied source snapshots, not a second semantic owner. Improve their
portable guidance in `agent-skills`; keep agent-dotfiles CLI details, private
prefix installation, and host projection details here.

## Maintainer synchronization

Only a maintainer preparing a reviewed agent-dotfiles change runs the local
synchronizer. It downloads nothing. It requires a separate clean local
`agent-skills` checkout at the exact reviewed full commit and refuses a dirty,
mismatched, missing, symlinked, or changed source file.

```sh
python3 tools/sync_portable_skills.py \
  --source /absolute/trusted/agent-skills \
  --revision APPROVED_AGENT_SKILLS_FULL_COMMIT_SHA \
  --destination /absolute/agent-dotfiles
```

Run it first with `--dry-run`, review `skills/portable-skills.json` and the
copied diff, then commit the synchronized result. A changed target file is a
refusal, not a silent overwrite. Consumer installation uses the ordinary pinned
agent-dotfiles installer; it verifies every copied file and the provenance
manifest before activation or removal.

## Consumer projection

After installing an approved agent-dotfiles prefix, a project that already uses
agent-loop can project the reviewed product and portable skills through the
existing explicit `install-assets` flow. The [project-onboarding guide](PROJECT_ONBOARDING.md)
shows the host-scoped Codex and Claude Code commands. Inspect the dry run before
the matching mutation. No selected skill is installed globally or activated by
default.

`language-onboarding-authoring` helps a team design another language-specific
skill. It does not create files, infer framework commands, or grant permission to
run project checks. Keep the resulting portable guidance with `agent-skills` or
the owning language/project repository; add a separate agent-dotfiles adapter
only when optional CLI or host integration is demonstrably needed.
