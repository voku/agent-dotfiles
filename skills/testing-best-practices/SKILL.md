---
name: testing-best-practices
description: Portable testing guidance for regression evidence, test structure, isolation, assertions, test data, test doubles, coverage strategy, and feedback speed. Use when writing or reviewing tests, fixing bugs, improving flaky suites, or planning test strategy; follow the target repository's existing framework and validation commands.
license: MIT
metadata:
  author: agent-skills
  version: "2.1.0"
---

# Testing Best Practices

Portable guidance for building useful, maintainable test evidence without turning one framework's habits or arbitrary metrics into universal laws.

## Grounding and Scope

Before changing tests, inspect the target repository's existing test framework, suite layout, fixtures/factories, CI tiers, database/environment setup, coverage tooling, and documented validation commands.

Prefer the nearest established test style unless it hides the behavior that needs evidence. Do not introduce a new framework, mocking library, fixture system, coverage threshold, or suite taxonomy merely because this skill contains an example of one.

## Canonical Rule Boundaries

### Test Structure
- [struct-aaa-pattern.md](rules/struct-aaa-pattern.md) - readable scenario structure, Arrange-Act-Assert/Given-When-Then flow, and one logical concept per test.
- [struct-lifecycle.md](rules/struct-lifecycle.md) - scoped setup/teardown and lifecycle ownership.

### Isolation
- [iso-independence.md](rules/iso-independence.md) - deterministic, order-independent tests and control of nondeterministic inputs.
- [iso-cleanup.md](rules/iso-cleanup.md) - cleanup of files, processes, listeners, environment state, database state, and other resources.

### Assertions
- [assert-specific.md](rules/assert-specific.md) - precise assertions with useful failure diagnostics.

### Test Data
- [data-factories.md](rules/data-factories.md) - factories/builders when they reduce setup noise while preserving intent.
- [data-minimal.md](rules/data-minimal.md) - minimal sufficient data plus realistic edge cases when behavior requires them.

### Test Doubles
- [mock-boundaries.md](rules/mock-boundaries.md) - choose mocks/fakes/stubs/spies/real collaborators according to stable seams and required evidence, not file boundaries alone.

### Coverage and Regression Evidence
- [cov-regression-first.md](rules/cov-regression-first.md) - reproduce bugs with the narrowest useful failing regression before changing production behavior when practical.
- [cov-edge-cases.md](rules/cov-edge-cases.md) - prioritize branches, boundaries, failure modes, and defect-prone behavior over vanity line coverage.

### Feedback Speed
- [perf-fast-unit.md](rules/perf-fast-unit.md) - measure feedback cost, remove accidental overhead, parallelize safely, and separate slower tiers only where useful.

## Test Expansion Discipline

- For a bug fix, prefer a failing regression that demonstrates the defect before modifying production code when the behavior can be reproduced safely and economically.
- For requests such as “more tests” or “more coverage”, identify a concrete branch, invariant, failure mode, or historically defect-prone path instead of optimizing a percentage in isolation.
- Set up only collaborators and data that matter to the behavior being tested.
- Prefer observable behavior over assertions about incidental implementation details.
- Use test doubles only when they preserve the evidence claim and reduce nondeterminism, destructive effects, unavailability, or irrelevant cost.
- Keep valuable integration/e2e evidence even when it is slower; optimize accidental cost before deleting meaningful coverage.

## Evidence Boundary

- A green test proves only the behavior actually exercised by that test and its environment.
- Coverage percentages show execution reach, not correctness or specification completeness.
- Flakiness is evidence of nondeterminism or environmental coupling that should be investigated, not automatically hidden with retries.
- “Unit”, “integration”, and “e2e” are useful scopes, not moral rankings. Use the cheapest scope that can still observe the behavior that matters.
- Do not invent successful test runs, coverage changes, or commands that were not actually executed.

## Projection Boundary

`README.md`, `AGENTS.md`, and `metadata.json` are supporting projections. If they disagree with this file or `rules/`, follow the canonical source and repair the projection. Do not copy a second current rule inventory, timing budget, framework recipe, or compiled example set into supporting projections.
