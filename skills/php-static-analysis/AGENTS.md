# PHP Static Analysis — Agent Projection

Implementation guidance for making PHP code provably typed under a strict static analyzer.

This file is a supporting agent projection. The canonical contract is `SKILL.md` plus `rules/`; do not infer the current rule inventory or independent semantics from this file.

## Fast path

1. Read `SKILL.md` to decide whether this skill applies.
2. Read only the relevant files under `rules/` for the current analyzer failure.
3. Classify the cause as a wrong contract or a missing proof.
4. Correct the owning boundary before adding local assertions or widening types.
5. Keep ignores, baselines, and analyzer extensions narrowly scoped.
6. Verify with the repository's configured analyzer command and report the observed result.

## Evidence contract

- Do not silence a real defect to make analysis green.
- Do not claim validation passed unless the analyzer result was actually observed.
- Do not invent a validation command when the repository does not define one.
- Preserve strict contracts when earlier boundary validation can provide the missing proof.

## Ownership boundary

`SKILL.md` owns scope, triggers, and routing. Files under `rules/` own detailed static-analysis semantics. This projection should stay compact and must not become a second compiled rule reference.
