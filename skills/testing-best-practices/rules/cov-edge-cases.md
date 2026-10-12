---
id: cov-edge-cases
title: Edge Cases, Error Paths, and Meaningful Coverage
category: cov
priority: MEDIUM
triggers: [100-percent-vanity-coverage, getter-setter-testing, untested-error-paths, unhandled-empty-null]
tags: [coverage, edge-cases, error-handling, unhappy-path, meaningful-coverage]
---

# Edge Cases, Error Paths & Meaningful Coverage

**Trigger Anchor:** Focus testing effort on decision branches, boundary values (null, empty, extremes), and error scenarios (thrown exceptions, rejected promises) rather than vanity line-coverage numbers.

---

## Meaningful Coverage vs Boilerplate Vanity Metrics

### Bad
```typescript
// ❌ Testing getters/setters and auto-generated glue solely to reach 100% line coverage
test('getter returns value', () => {
  const model = new UserModel('123');
  expect(model.getId()).toBe('123');
});
```

### Good
```typescript
// ✅ Targeting high-risk decision rules and calculations
test('applies tiered volume discount over threshold', () => {
  const engine = new PricingEngine();
  expect(engine.calculate(9, 100)).toBe(900);
  expect(engine.calculate(10, 100)).toBe(850); // 15% discount threshold
});
```

---

## Boundary Values & Edge Inputs

### Bad
```typescript
// ❌ Happy path only: assumes non-empty array with positive numbers
test('finds maximum', () => {
  expect(findMax([1, 2, 3])).toBe(3);
});
```

### Good
```typescript
// ✅ Boundary conditions: empty sets, negative numbers, duplicates, and extremes
describe('findMax', () => {
  it('throws on empty array', () => {
    expect(() => findMax([])).toThrow('Array cannot be empty');
  });

  it('handles negative integers and duplicates', () => {
    expect(findMax([-5, -1, -1])).toBe(-1);
  });
});
```

---

## Unhappy Paths & Error Scenarios

### Bad
```typescript
// ❌ Ignoring failure responses, timeouts, and network rejections
test('charges card', async () => {
  const res = await chargeCard('tok_valid', 50);
  expect(res.status).toBe('succeeded');
});
```

### Good
```typescript
// ✅ Explicit verification of thrown domain errors and rejection handling
describe('chargeCard error paths', () => {
  it('throws InsufficientFundsError when card has no balance', async () => {
    mockGateway.charge.mockRejectedValue(new Error('insufficient_funds'));

    await expect(chargeCard('tok_broke', 50)).rejects.toThrow(InsufficientFundsError);
  });

  it('rejects non-positive payment amounts synchronously', () => {
    expect(() => chargeCard('tok_valid', -10)).toThrow('Amount must be positive');
  });
});
```
