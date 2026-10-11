---
id: sa-contract-honesty
title: "Contract Honesty Over False Widening"
category: contracts
priority: HIGH
triggers: [weakened-contract-type, proof-gap-widening, false-nullable-return, non-empty-downgrade]
tags: [phpstan, static-analysis, contracts, type-proof, boundary-validation]
---

# Contract Honesty Over False Widening

**Trigger Anchor:** Distinguish a genuine contract defect from a static proof gap; never weaken a strict return or parameter type (`non-empty-string`, `int`, `T`) merely to silence an analyzer error—supply the runtime proof or boundary validation instead.

---

### Bad
```php
// ❌ Widening a strict contract because analyzer cannot prove non-empty
class TableMetadata
{
    // Widened from non-empty-string to string to make PHPStan error disappear
    public function getTableName(): string // Lost non-empty-string contract for all callers!
    {
        return $this->table;
    }
}

// ❌ Bypassing null check by falsely claiming method always returns entity
class OrderFinder
{
    // Analyzer warns that DB::find can return null, so dev relaxes or forces type:
    /** @var Order */
    public function find(int $id): Order // Lies about nullability!
    {
        return DB::find($id); // Actually returns ?Order!
    }
}
```

### Good
```php
// ✅ Maintain strict contract and provide validation proof at the boundary
class TableMetadata
{
    /**
     * @param non-empty-string $table
     */
    public function __construct(
        private string $table,
    ) {
        if ($table === '') {
            throw new \InvalidArgumentException('Table name must not be empty.');
        }
    }

    /**
     * @return non-empty-string
     */
    public function getTableName(): string
    {
        return $this->table; // Proven non-empty by construction
    }
}

// ✅ Honest nullable contract with explicit exception helper for strict callers
class OrderFinder
{
    public function find(int $id): ?Order
    {
        return DB::find($id);
    }

    public function findOrFail(int $id): Order
    {
        return $this->find($id) ?? throw new OrderNotFoundException($id);
    }
}
```
