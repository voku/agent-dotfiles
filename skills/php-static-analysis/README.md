# PHP Static Analysis

Implementation guidance for making PHP code provably typed under a strict static analyzer.

This README is a supporting projection. The canonical contract is `SKILL.md` plus `rules/`; use those files for the current rule inventory and detailed semantics.

## When to use

Apply this skill when:

- PHPStan or Psalm reports a typing problem that should be fixed rather than hidden;
- an API, collection, factory, or dynamic helper needs a more precise analyzable contract;
- repeated inline assertions suggest the producer or owner boundary is under-typed;
- an ignore, baseline entry, or analyzer extension needs to be scoped deliberately.

## Fast path

1. Detect the project's PHP and analyzer configuration.
2. Decide whether the defect is a wrong contract or a missing proof.
3. Fix the owning boundary before adding caller-side assertions.
4. Prefer native PHP types, then precise PHPDoc shapes/generics where native types are insufficient.
5. Keep suppressions narrow and explain why they remain necessary.
6. Verify with the repository's own analyzer command and report only observed results.

## Ownership boundary

`SKILL.md` owns the compact scope, triggers, and routing. Files under `rules/` own the detailed static-analysis guidance. This README must not become a second rule catalog or carry independent rule counts.

`code-review-type-safety` is the review counterpart: it identifies weak contracts in a diff. `php-static-analysis` is the implementation guidance for correcting them.
