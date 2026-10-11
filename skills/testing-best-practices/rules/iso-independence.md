---
id: iso-independence
title: Test Independence and Determinism
category: iso
priority: CRITICAL
triggers: [shared-mutable-state, order-dependent-tests, cascading-failures, flaky-clock, real-setTimeout, race-condition]
tags: [test-isolation, independence, deterministic, no-shared-state, order-independence, test-doubles]
---

# Test Independence & Determinism

**Trigger Anchor:** Tests must be self-contained and deterministic—pass in any execution order, share zero mutable state, freeze time/randomness, and isolate from external systems with test doubles.

---

## Shared Mutable State & Order Independence

### Bad
```typescript
// ❌ Shared module-level state: test 2 silently depends on test 1 executing first
const cart = new ShoppingCart();

test('adds initial item', () => {
  cart.addItem({ id: '1', price: 10 });
  expect(cart.getItemCount()).toBe(1);
});

test('calculates total with subsequent item', () => {
  // Fails if executed alone or in randomized order
  cart.addItem({ id: '2', price: 20 });
  expect(cart.getTotal()).toBe(30);
});
```

### Good
```typescript
// ✅ Fresh instance per test: can run individually, randomized, or concurrently
describe('ShoppingCart', () => {
  let cart: ShoppingCart;

  beforeEach(() => {
    cart = new ShoppingCart();
  });

  test('adds initial item', () => {
    cart.addItem({ id: '1', price: 10 });
    expect(cart.getItemCount()).toBe(1);
  });

  test('calculates total for multiple items', () => {
    cart.addItem({ id: '1', price: 10 });
    cart.addItem({ id: '2', price: 20 });
    expect(cart.getTotal()).toBe(30);
  });
});
```

---

## Determinism & Test Doubles (Time, Randomness, Network)

### Bad
```typescript
// ❌ Flaky: depends on real system clock, network call, and real delay
test('expires session after 24h', async () => {
  const session = createSession();
  await new Promise(r => setTimeout(r, 86400000)); // Unrunnable
  expect(session.isExpired()).toBe(true);
});
```

### Good
```typescript
// ✅ Controlled clock and injected double make execution instant and deterministic
test('expires session after 24h', () => {
  const mockClock = { now: vi.fn() };
  const initialTime = new Date('2026-01-01T12:00:00Z');
  const expiredTime = new Date('2026-01-02T12:00:01Z');

  mockClock.now.mockReturnValue(initialTime);
  const session = createSession({ clock: mockClock });

  mockClock.now.mockReturnValue(expiredTime);
  expect(session.isExpired()).toBe(true);
});
```
