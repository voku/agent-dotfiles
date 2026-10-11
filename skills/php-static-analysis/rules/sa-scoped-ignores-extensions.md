---
id: sa-scoped-ignores-extensions
title: "Scoped Ignores, Baseline Discipline, and Dynamic Extensions"
category: ignores-extensions
priority: MEDIUM
triggers: [broad-baseline-suppression, unscoped-phpstan-ignore, missing-ignore-identifier, dynamic-method-reflection]
tags: [phpstan, static-analysis, baselines, ignore-errors, phpstan-extensions]
---

# Scoped Ignores, Baseline Discipline, and Dynamic Extensions

**Trigger Anchor:** Scope `@phpstan-ignore` annotations to the exact line and error identifier with a documented justification; use PHPStan dynamic return type extensions or class reflection stubs instead of blanket directory-level baseline suppressions.

---

### Bad
```php
// ❌ Blanket baseline or unscoped ignore without identifier or reason
// @phpstan-ignore-next-line (What error is ignored? Why is it safe?)
$result = $magicProxy->callDynamicMethod();

// In phpstan.neon:
// ignoreErrors:
//   - '#.*#' # Silences everything!
```

### Good
```php
// ✅ Scoped ignore with explicit identifier and explanatory comment
// @phpstan-ignore method.notFound (Dynamic method handled by legacy magic __call fallback)
$result = $magicProxy->callDynamicMethod();

// ✅ Or better: write a PHPStan DynamicMethodReturnTypeExtension for dynamic proxies:
class MagicProxyReturnTypeExtension implements \PHPStan\Type\DynamicMethodReturnTypeExtension
{
    public function getClass(): string { return MagicProxy::class; }
    public function isMethodSupported(\PHPStan\Reflection\MethodReflection $m): bool {
        return $m->getName() === 'callDynamicMethod';
    }
    public function getTypeFromMethodCall(\PHPStan\Reflection\MethodReflection $m, \PhpParser\Node\Expr\MethodCall $c, \PHPStan\Analyser\Scope $s): \PHPStan\Type\Type {
        return new \PHPStan\Type\StringType();
    }
}
```
