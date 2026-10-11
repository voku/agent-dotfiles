---
id: assert-specific
title: Specific Matchers and Domain Assertions
category: assert
priority: HIGH
triggers: [generic-boolean-assertions, reversed-expected-actual, magic-numbers-in-assert, duplicate-assertion-blocks, cryptic-failure-messages]
tags: [assertions, specific, matchers, expected-actual, constants, custom-matchers]
---

# Specific Matchers & Domain Assertions

**Trigger Anchor:** Assert exact intent and meaningful failure contracts using specific matchers, standard `expect(actual).toBe(expected)` order, named domain constants, and reusable custom matchers.

---

## Specific Matchers & Framework Convention

### Bad
```typescript
// ❌ Generic boolean assertions, reversed actual/expected, and fragile serialization
test('validates user response', async () => {
  const res = await userService.getUser('1');
  expect(res !== null).toBe(true); // "expected true, got false" on failure
  expect('Alice').toBe(res.name);   // Reversed: expected 'Alice', got undefined
  expect(JSON.stringify(res).includes('admin')).toBe(true);
});
```

### Good
```typescript
// ✅ Precise matchers with expect(actual).toBe(expected) order
test('validates user response', async () => {
  const res = await userService.getUser('1');
  expect(res).not.toBeNull();
  expect(res.name).toBe('Alice');
  expect(res).toMatchObject({ role: 'admin' });
});
```

---

## Domain Constants vs Magic Numbers

### Bad
```typescript
// ❌ Unexplained magic numbers obscure business reasoning
test('applies promotion cap', () => {
  const discount = calculator.getDiscount(1000, 'SUMMER_DEAL');
  expect(discount).toBe(150); // Why 150? Formula is opaque.
});
```

### Good
```typescript
// ✅ Named constants and explicit calculation reveal business rules
test('applies promotion cap', () => {
  const ORDER_SUBTOTAL = 1000;
  const MAX_DISCOUNT_CAP = 150;

  const discount = calculator.getDiscount(ORDER_SUBTOTAL, 'SUMMER_DEAL');

  expect(discount).toBe(MAX_DISCOUNT_CAP);
});
```

---

## Reusable Custom Matchers

### Bad
```typescript
// ❌ Repeating multi-line assertions across dozens of test cases
test('order status is pending', () => {
  expect(order.status).toBe('pending');
  expect(order.paidAt).toBeNull();
  expect(order.shippedAt).toBeNull();
  expect(order.items.length).toBeGreaterThan(0);
});
```

### Good
```typescript
// ✅ Custom domain matcher with expressive failure messages
expect.extend({
  toBePendingOrder(received: Order) {
    const pass = received.status === 'pending' && received.paidAt === null && received.items.length > 0;
    return {
      pass,
      message: () => `Expected order to be in pending state with items, but got status="${received.status}"`
    };
  }
});

test('order status is pending', () => {
  expect(order).toBePendingOrder();
});
```
