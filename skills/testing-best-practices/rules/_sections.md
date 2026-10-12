# Sections

This file groups the canonical testing rules by concern. The individual non-underscore files in this directory own the detailed rule semantics.

## Test Structure (`struct`)

**Impact:** CRITICAL

Scenario-focused organization, readable Arrange-Act-Assert or Given-When-Then flow, and scoped lifecycle setup/teardown.

## Test Isolation (`iso`)

**Impact:** CRITICAL

Deterministic, order-independent tests without unintended shared mutable state or leaked resources.

## Assertions (`assert`)

**Impact:** HIGH

Specific assertions that express the behavior under test clearly and fail with useful diagnostics.

## Test Data (`data`)

**Impact:** HIGH

Minimal sufficient inputs, reusable factories/builders where they reduce noise, and realistic edge-case data when the behavior requires it.

## Test Doubles (`mock`)

**Impact:** MEDIUM

Mocks, fakes, stubs, spies, and real collaborators chosen according to stable seams, determinism, cost, and the evidence the test must preserve. Avoid coupling tests to incidental implementation decomposition.

## Coverage and Regression Evidence (`cov`)

**Impact:** HIGH

Regression-first reproduction for bugs, decision branches, edge/error paths, and meaningful behavioral coverage rather than vanity line percentages.

## Feedback Speed (`perf`)

**Impact:** LOW

Measured feedback-loop performance, removal of accidental waits/overhead, safe concurrency when isolation permits, and useful separation of slower test tiers where it improves workflow or CI control.
