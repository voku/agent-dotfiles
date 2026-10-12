---
id: struct-aaa-pattern
title: Arrange-Act-Assert and Specification Structure
category: struct
priority: CRITICAL
triggers: [interleaved-setup-assertions, multi-behavior-test, vague-test-names, missing-describe-context, technical-test-names]
tags: [test-structure, aaa, arrange-act-assert, describe-it, given-when-then, single-assertion]
---

# Arrange-Act-Assert & Specification Structure

**Trigger Anchor:** Structure tests around Arrange-Act-Assert (or Given-When-Then), using descriptive scenario-focused naming and verifying one logical concept per test.

---

## AAA Flow & Single Assertion

### Bad
```typescript
// ❌ Interleaved setup, execution, and multiple unrelated assertions
test('cart operations', () => {
  const cart = new ShoppingCart();
  expect(cart.isEmpty()).toBe(true);
  cart.addItem({ name: 'Book', price: 20 });
  cart.applyDiscount(0.1);
  expect(cart.getTotal()).toBe(18);
  expect(cart.getItemCount()).toBe(1);
  expect(sendCartMetric).toHaveBeenCalledWith('item_added');
});
```

### Good
```typescript
// ✅ Explicit AAA phases testing one logical concept per test
describe('ShoppingCart.getTotal', () => {
  it('applies percentage discount to cart total', () => {
    // Arrange
    const cart = new ShoppingCart();
    cart.addItem({ name: 'Book', price: 20 });
    cart.applyDiscount(0.1);

    // Act
    const total = cart.getTotal();

    // Assert
    expect(total).toBe(18);
  });
});
```

---

## Hierarchical & Descriptive Specifications

### Bad
```typescript
// ❌ Flat, cryptic test names without business scenario context
test('test1', () => expect(validateEmail('test@test.com')).toBe(true));
test('calc error', () => expect(() => divide(10, 0)).toThrow());
```

### Good
```typescript
// ✅ Hierarchical describe/it blocks acting as executable specifications
describe('Calculator', () => {
  describe('divide', () => {
    it('returns quotient when dividing two positive numbers', () => {
      expect(divide(10, 2)).toBe(5);
    });

    it('throws DivisionByZeroError when denominator is zero', () => {
      expect(() => divide(10, 0)).toThrow(DivisionByZeroError);
    });
  });
});
```

---

## Behavior-Driven (Given-When-Then)

### Bad
```typescript
// ❌ Technical, procedural test obscuring customer-facing outcome
test('order submit', () => {
  const order = new Order({ id: 1, total: 100 });
  const res = order.submit();
  expect(res.status).toBe('confirmed');
  expect(emailService.send).toHaveBeenCalled();
});
```

### Good
```typescript
// ✅ BDD structure mapping directly to acceptance criteria
describe('Order Submission', () => {
  describe('given an order with valid payment details', () => {
    it('confirms the order and dispatches customer notification', () => {
      const order = OrderFactory.createReadyToSubmit();

      const result = order.submit();

      expect(result.status).toBe('confirmed');
      expect(emailService.sendConfirmation).toHaveBeenCalledWith(order.id);
    });
  });
});
```
