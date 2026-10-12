# Testing Best Practices

Portable testing guidance for regression evidence, test structure, isolation, assertions, test data, test doubles, coverage strategy, and feedback speed.

## Canonical Source

`SKILL.md` defines activation, decision discipline, evidence boundaries, and rule routing. The non-underscore files under `rules/` contain the canonical detailed guidance. This README is a routing projection only; it must not own a second rule inventory, count, timing budget, framework recipe, or compiled example set.

## When to Use

Use this skill when writing or reviewing tests, fixing bugs, investigating flaky suites, improving meaningful coverage, or planning test strategy.

## Routing

1. Inspect the target repository's existing framework, test layout, fixtures/factories, CI tiers, and validation commands.
2. Read `SKILL.md` first.
3. Load only the canonical rule files relevant to the behavior under test.
4. Prefer observable behavior and the smallest test scope that still provides the needed evidence.
5. Run the repository-owned validation commands and report only evidence actually observed.

## Projection Boundary

If this file disagrees with `SKILL.md` or `rules/`, follow the canonical source and repair this projection. Do not copy current rule IDs, counts, framework-specific recipes, fixed performance targets, or long examples back into this file.
