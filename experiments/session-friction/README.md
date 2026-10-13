# Session friction experiment

This directory is an experiment, not part of the installed agent-dotfiles
runtime.

The working coding agent should concentrate on its real task. It is not asked to
remember friction, write Learning notes, or carry a catalog of agent-dotfiles
features in its prompt.

Instead, a separate post-hoc pass reads session traces and flags mechanical
patterns that may be worth a human look.

## First experiment

`tools/session_friction.py` reads local JSON or JSONL files and emits a JSON
report to stdout.

It currently recognizes:

- repeated identical commands,
- the same failing command more than once,
- multiple failed variants of the same executable,
- repeated file reads,
- repeated searches.

Those are **candidate friction signals**, not recommendations. A repeated command
may be completely reasonable. The analyzer does not edit dotfiles, write
Memory/Learning state, modify a repository, or upload telemetry.

Example with a normalized fixture:

```json
{"kind":"command","value":"git status --short","success":true}
{"kind":"command","value":"git status --short","success":true}
{"kind":"command","value":"git status --short","success":true}
```

```sh
python3 tools/session_friction.py --input-format normalized trace.jsonl --pretty
```

The default `auto` mode also performs deliberately small, best-effort
extraction from nested tool-call records such as an `exec_command` /
`arguments.command` shape or a `Bash` / `input.command` shape. These are
not yet claimed as stable Codex or Claude Code adapters. Exact host adapters
must be derived from real current traces, not invented schemas.

## Privacy

Session traces may contain source code, prompts, credentials, file paths, or
customer data.

- Run this tool locally.
- Do not commit raw traces or generated reports.
- Review report output before sharing it.
- The tool redacts common token/password/secret command arguments in candidate
  samples, but this is defense in depth, not a complete secret scanner.
- No network calls are made.

## Human review loop

For roughly ten real sessions across Codex and Claude Code:

1. let the coding agent work normally;
2. analyze the trace afterwards;
3. inspect candidates, not the whole session unless needed;
4. classify each useful candidate as:
   - environment/default friction,
   - native shortcut opportunity,
   - project-specific behavior,
   - already solved by newer agent capability,
   - noise;
5. change agent-dotfiles only for recurring environment/default or shortcut
   patterns that still matter.

The important asymmetry is intentional: the task agent does not have to notice
or remember the improvement opportunity. The separate reviewer does.

## Stop condition

After about ten real sessions, decide whether this experiment found repeated,
actionable patterns.

If it did, add only the smallest host-specific adapters or dotfile improvements
needed by the evidence. If it did not, leave this experimental or delete it.
Do not grow a trace-analysis framework merely because parsing JSON is
emotionally soothing to software developers.
