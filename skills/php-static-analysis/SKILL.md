---
name: php-static-analysis
description: Implementation guidance for making PHP code provably typed under a strict static analyzer - native types first, precise array shapes and generics, honest contracts, scoped ignores, and analyzer extensions instead of inline casts. Triggers on "phpstan error", "psalm error", "type precision", "array shape", "class-string", "baseline", and related static-analysis work.
license: MIT
metadata:
  author: Agent Skills Team
  version: "2.0.0"
---

# PHP Static Analysis

Implementation guidance for raising the precision of PHP code under a strict static analyzer (PHPStan / Psalm). Contains 5 consolidated, high-density rules.

## Quick Reference

| Priority | Category | Rule File | Primary Focus |
|----------|----------|-----------|---------------|
| **CRITICAL** | Native Types First | [`sa-native-types-first`](rules/sa-native-types-first.md) | Native PHP types on properties/parameters, strict comparisons (`===`), no loose downgrades |
| **CRITICAL** | Shape Precision | [`sa-shape-precision`](rules/sa-shape-precision.md) | `array{...}`, `list<T>`, `class-string<T>`, and `non-empty-string` over loose `mixed` |
| **HIGH** | Contract Honesty | [`sa-contract-honesty`](rules/sa-contract-honesty.md) | Supplying boundary validation proof instead of relaxing or widening strict contracts |
| **HIGH** | Root-Cause Typing | [`sa-root-cause-typing`](rules/sa-root-cause-typing.md) | Typing producers and factory generics at the source instead of repetitive inline `@var` casts |
| **MEDIUM** | Scoped Ignores | [`sa-scoped-ignores-extensions`](rules/sa-scoped-ignores-extensions.md) | Scoped `@phpstan-ignore` with identifiers and reasons, dynamic return type extensions |

---

## When to Apply

Reference these guidelines when:
- An analyzer error must be resolved without weakening the contract
- A public API, factory, or collection helper needs an analyzable signature
- Inline casts, `@var` annotations, or a growing baseline are being used to keep the build green
- A repository is raising its analysis level and needs an order of attack

## Scope Discipline

### In Scope
- Typing decisions in the code under change and its direct call sites
- The smallest contract change that makes the analyzer's claim true
- Deciding between a wrong contract and a proof gap
- Keeping an existing strict contract intact while narrowing inputs earlier

### Out of Scope
- Repository-wide type migrations that were not requested
- Style or naming changes unrelated to the reported error
- Silencing an error whose underlying behavior is genuinely wrong - that is a bug, not a typing task

## Output Format

State, per finding: the analyzer message, the real cause (wrong contract or missing proof), the chosen fix at its owning layer, and the command that verified it. Claim a pass only after observing the analyzer's exit code on the changed scope.
