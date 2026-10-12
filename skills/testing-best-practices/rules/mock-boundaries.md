---
id: mock-boundaries
title: Use Test Doubles at Stable Seams
category: mock
priority: MEDIUM
triggers: [mocking-internal-utils, over-mocking-logic, unverified-mock-calls, incomplete-mock-payloads, mock-returns-true]
tags: [mocking, seams, boundaries, minimal-mocking, contracts, verification]
---

# Use Test Doubles at Stable Seams

**Trigger Anchor:** Prefer behavior-focused tests that exercise real application logic. Introduce mocks, fakes, stubs, or spies at stable seams when the real collaborator would make the test nondeterministic, destructive, unavailable, prohibitively slow, or unable to isolate the behavior under test. Avoid mocking implementation details merely because they are easy to replace.

External systems such as HTTP services, databases, queues, clocks, filesystems, and process boundaries are common seams, but they are not the only legitimate ones. The target repository's architecture determines where an owned seam actually exists.

---

## Behavior vs Implementation Coupling

### Bad
```typescript
// ❌ Internal helpers are mocked only to mirror today's file decomposition.
vi.mock('./tax-calculator', () => ({ calculateTax: vi.fn().mockReturnValue(10) }));
vi.mock('./format-currency', () => ({ formatCurrency: vi.fn().mockReturnValue('$110') }));

test('processes order', () => {
  const result = processOrder({ price: 100 });
  expect(result.formatted).toBe('$110');
});
```

The test can stay green while the real calculation is broken, and harmless refactoring of helper boundaries now breaks the test.

### Better
```typescript
// ✅ Real domain logic runs; only the owned payment seam is replaced.
test('calculates total and charges the payment gateway', async () => {
  const gateway = { charge: vi.fn().mockResolvedValue({ id: 'txn_1', status: 'paid' }) };
  const processor = new OrderProcessor(gateway);

  const result = await processor.processOrder({ price: 100, taxRate: 0.1 });

  expect(result.total).toBe(110);
  expect(gateway.charge).toHaveBeenCalledWith(110);
});
```

Mock interactions only when the interaction itself is part of the contract. Prefer asserting observable results when call order/count is merely an implementation detail.

---

## Realistic Boundary Simulation

When replacing an HTTP or message boundary, keep the fake contract realistic enough to catch schema/status/error assumptions. A protocol-level tool such as MSW can be useful for frontend/HTTP-client tests, but it is an option rather than a required library.

For database behavior, use an integration test with the real supported database when SQL semantics, constraints, transactions, migrations, or mapping are the behavior under test. A repository fake is appropriate when the application decision is the subject and persistence behavior is deliberately outside that test's scope.

## Selection Rule

Choose the cheapest test double that preserves the evidence needed by the test:

- **fake** for a lightweight working implementation;
- **stub** for controlled inputs/results;
- **spy/mock** when an interaction is an observable contract;
- **real collaborator** when substituting it would hide the behavior being verified.

Do not make a test more isolated than its claim can support.
