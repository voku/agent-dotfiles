# Rule Sections

## Priority Levels

| Level | Description | When to Apply |
|-------|-------------|---------------|
| CRITICAL | Native PHP types and precise array shapes/generics | Property declarations, method signatures, and complex data structures |
| HIGH | Contract honesty and root-cause typing at the source | Boundary validations and factory/service return types |
| MEDIUM | Scoped ignores and dynamic analyzer extensions | Legacy integration points and dynamic metaprogramming |

## Section Overview

### 1. Native Types First (`native-types`)
- **Impact:** CRITICAL
- **Rules:** `sa-native-types-first`
- **Description:** Declaring native types on class properties and parameters before PHPDoc; preserving strict comparisons (`===`).

### 2. Shape & Generic Precision (`shapes`)
- **Impact:** CRITICAL
- **Rules:** `sa-shape-precision`
- **Description:** Precise array shapes (`array{...}`), lists (`list<T>`), and generics (`class-string<T>`) over loose `mixed`.

### 3. Contract Honesty (`contracts`)
- **Impact:** HIGH
- **Rules:** `sa-contract-honesty`
- **Description:** Maintaining strict return types and supplying boundary validation proof rather than relaxing contracts.

### 4. Root-Cause Typing (`root-cause`)
- **Impact:** HIGH
- **Rules:** `sa-root-cause-typing`
- **Description:** Typing producers and factories at the source instead of repeating inline `@var` assertions at caller sites.

### 5. Scoped Ignores & Extensions (`ignores-extensions`)
- **Impact:** MEDIUM
- **Rules:** `sa-scoped-ignores-extensions`
- **Description:** Scoped `@phpstan-ignore` annotations with identifiers and reasons; dynamic return type extensions.
