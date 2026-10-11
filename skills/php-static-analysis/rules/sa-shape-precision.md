---
id: sa-shape-precision
title: "Array Shape Precision, Lists, and Advanced Type Narrowing"
category: shapes
priority: CRITICAL
triggers: [untyped-array-parameter, missing-array-shape, mixed-collection, non-empty-string-proof, class-string-generic]
tags: [phpstan, static-analysis, array-shapes, generics, lists, type-narrowing]
---

# Array Shape Precision, Lists, and Advanced Type Narrowing

**Trigger Anchor:** Replace bare `array` and `mixed` with precise array shapes (`array{id: int, name: string}`), `list<T>`, `class-string<T>`, and `non-empty-string` to document and prove data structure contracts to the analyzer.

---

### Bad
```php
// ❌ Bare array obscures required structure and allows missing key bugs
class UserExporter
{
    /**
     * @param array $users
     * @return array
     */
    public function formatExport(array $users): array
    {
        $result = [];
        foreach ($users as $u) {
            // Analyzer cannot verify if 'id' or 'email' exist!
            $result[] = $u['id'] . ':' . $u['email'];
        }
        return $result;
    }
}
```

### Good
```php
// ✅ Precise PHPDoc shapes and lists proving key existence and element types
class UserExporter
{
    /**
     * @param list<array{id: int, email: non-empty-string, name?: string}> $users
     * @return list<string>
     */
    public function formatExport(array $users): array
    {
        $result = [];
        foreach ($users as $u) {
            $result[] = $u['id'] . ':' . $u['email'];
        }
        return $result;
    }

    /**
     * @template T of object
     * @param class-string<T> $className
     * @return T
     */
    public function instantiate(string $className): object
    {
        return new $className();
    }
}
```
