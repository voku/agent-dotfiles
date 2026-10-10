# Quality-first preflight before the agent-loop A/B run

## Observed bugs in the initial baseline

1. `git-patch a[1].php` could include unrelated changes from `a1.php`
   because native Git pathspecs treat brackets and stars as patterns.
2. `git-patch new.php` returned a successful, empty, `truncated:false`
   patch for new/ignored files. Native Git excludes these files from `diff`,
   so the empty patch could be mistaken for proof that nothing changed.
3. Selecting a directory (including a directory removed from the worktree)
   could return changes from several files under a one-file JSON contract.

These were reproduced against real Git, not inferred from mocks.

## New evidence contract

- `git-patch FILE` uses literal Git pathspecs and verifies that a nonempty
  patch contains changes for **exactly that path** via Git's NUL-delimited
  name-only output; mismatches produce `ambiguous_path`, exit 2.
- A truly unchanged **indexed** path may produce a complete empty patch.
  An untracked, ignored or absent path produces `path_not_in_diff`, exit 2,
  with instructions to use `read` and `git-status`. This is an intentional
  fail-closed behavioral correction. `read` remains available for the
  untracked source, preserving relevant context.
- Patch bytes, SHA-256, binary fallback and the existing output cap remain
  unchanged. No transparent interception or global Git configuration change.

## Reproducible preflight

```sh
python -m unittest discover -s tests -p test_context_quality.py -v
python -m unittest discover -s tests -v
# Independently in GitHub Actions: Bashunit integration tests.
```

The real-Git fixtures test literal brackets/stars, unrelated modified files,
untracked and ignored sources, clean indexed files, deletion, staged addition
and nonexistent/removed directories.

## A/B priority order

1. **Quality gate:** find all required files and retrieve only the intended
   source/diff evidence. Reject incorrect scope, missing relevant context,
   silent partial results and untrusted-execution risks.
2. **Task correctness:** the agent fixes/diagnoses the problem with the
   required validation and review evidence.
3. **Total cost:** compare the full baseline-versus-tool task, including
   rereads, retries, extra tool invocations, wall time and observed tokens.
   Do not infer end-to-end savings from one shorter terminal response.
4. **Re-run:** apply a measured improvement, test a fresh consumer session,
   and record whether the benefit persists.

This preflight supplies deterministic correctness receipts, **not** evidence
that an LLM-powered consumer improves task completion. That still requires
the independent A/B and second fresh session in agent-loop#757.
