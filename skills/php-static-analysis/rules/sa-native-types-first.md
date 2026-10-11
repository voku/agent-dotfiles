---
id: sa-native-types-first
title: "Native Types First and Strict Comparison Invariants"
category: native-types
priority: CRITICAL
triggers: [missing-property-type, unsafe-strict-comparison, loose-equality-downgrade, redundant-phpdoc-type]
tags: [phpstan, static-analysis, native-types, strict-comparison, active-row, php]
---

# Native Types First and Strict Comparison Invariants

**Trigger Anchor:** Declare native PHP types on properties, parameters, and returns before reaching for PHPDoc annotations; never downgrade `===` to `==` to bypass untyped property comparisons—declare the native property type on the owning class instead.

---

### Bad
```php
// ❌ Untyped property leads to static analysis warning on strict comparison;
// downgrading to loose equality hides type drift and introduces subtle bugs
class AccountActiveRow
{
    public $is_active; // Untyped property
}

// Bypassing itportal.activerow.unsafeStrictComparison by loosening to ==:
if ($row->is_active == 1) { ... } // ❌ Loose equality bypasses analyzer but introduces coercion bugs!

// ❌ Using inline @var instead of declaring the property type
/** @var int $count */
$count = (int)$row->count;
```

### Good
```php
// ✅ Explicit native property types enable safe, strict comparisons
class AccountActiveRow
{
    public int $id;
    public int $is_active;
    public ?string $email = null;
}

// Strict comparison succeeds cleanly without analyzer error or runtime coercion risk
if ($row->is_active === 1) {
    // Exact integer match guaranteed
}

// ✅ Declared on source, so every reader inherits the type without inline casting
$count = $row->id;
```
