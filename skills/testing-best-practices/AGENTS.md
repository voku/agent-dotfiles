# Testing Best Practices - Agent Projection

This file is a compact routing projection. The canonical contract is `SKILL.md` plus the non-underscore rule files under `rules/`. Do not maintain a second rule inventory, timing budget, framework recipe, or compiled example set here.

## Fast Path

1. Inspect the target repository's test framework, suite layout, fixtures/factories, CI tiers, database/environment setup, and validation commands.
2. Read `SKILL.md` first and load only the relevant canonical rules.
3. For bug fixes, prefer a minimal failing regression before production changes when practical.
4. Choose the cheapest test scope and collaborator strategy that still preserves the evidence claim.
5. Run repository-owned validation and report only observed failures/passes/coverage evidence.

## Ownership Boundary

- `SKILL.md` owns activation, rule routing, test-expansion discipline, and evidence limits.
- `rules/` owns detailed testing guidance.
- the target repository owns framework choice, suite taxonomy, fixtures, thresholds, CI commands, supported databases/environments, and acceptance criteria.
- this projection owns no independent testing semantics.

## Evidence Boundary

- Coverage percentage is not correctness.
- A fast test is not automatically a good test, and a slow integration test is not automatically waste.
- Do not impose a universal millisecond budget.
- Prefer stable seams and observable behavior over mocks of incidental implementation structure.
- Test doubles are tools, not a requirement to fake every external collaborator or a prohibition against replacing an owned internal seam.
- Parallelism is useful only when isolation and resource constraints make it safe.
- Retries must not be used to hide unexplained nondeterminism.
- Never claim a test run or coverage result that was not actually observed.

## Projection Boundary

If this file disagrees with `SKILL.md`, `rules/`, or stronger repository/task instructions, follow the authoritative source and repair this projection. Do not copy current rule IDs, counts, framework-specific recipes, fixed timing targets, or long examples back into this file.
