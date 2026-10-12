---
id: perf-fast-unit
title: Feedback Speed, Concurrency, and Test Tiers
category: perf
priority: LOW
triggers: [slow-unit-tests, sequential-test-suite, flat-test-directory, sleep-in-tests]
tags: [performance, feedback-loop, parallel, concurrency, tiers]
---

# Feedback Speed, Concurrency & Test Tiers

**Trigger Anchor:** Keep the relevant test feedback loop fast enough for the repository's workflow. Measure actual cost before optimizing, remove avoidable sleeps/network/process overhead, parallelize only when isolation permits it, and separate slower test tiers when that materially improves feedback or CI control.

There is no universal per-test millisecond budget. A useful unit test is usually cheap because it exercises a small deterministic boundary, but correctness and useful evidence outrank an arbitrary timing threshold.

---

## Avoid Accidental External Cost in Unit-Level Tests

### Bad
```typescript
// ❌ A unit-level behavior test pays for a real database even though persistence is not under test.
test('creates user', async () => {
  const pool = new Pool({ connectionString: 'postgres://localhost/test' });
  const res = await pool.query('INSERT INTO users(name) VALUES ($1) RETURNING *', ['Alice']);
  expect(res.rows[0].name).toBe('Alice');
});
```

### Better
```typescript
// ✅ Use a cheap collaborator when the behavior under test is service logic, not database integration.
test('passes the created user to persistence', async () => {
  const repository = { save: vi.fn(async (user) => user) };
  const service = new UserService(repository);

  const user = await service.create({ id: 'u-1', name: 'Alice' });

  expect(repository.save).toHaveBeenCalledWith(user);
});
```

Use a real database in an integration test when database behavior, schema constraints, transactions, queries, or mapping are the thing that needs evidence.

---

## Concurrency and Test Tiers

Parallel execution is useful only when the tests are isolated enough to run safely. Shared ports, databases, files, rate limits, global process state, or resource contention may require explicit isolation or selective serialization.

Split unit/integration/e2e suites when the distinction improves developer feedback, CI scheduling, ownership, or failure diagnosis. Do not create tiers merely to satisfy a naming convention.

When a suite is slow:

1. measure which tests or setup phases dominate runtime;
2. remove accidental waits, repeated expensive setup, or unnecessary external dependencies;
3. fix isolation before enabling more concurrency;
4. parallelize where the repository and runner can safely benefit;
5. keep slower high-value integration/e2e evidence rather than deleting it just to make a timing number look better.
