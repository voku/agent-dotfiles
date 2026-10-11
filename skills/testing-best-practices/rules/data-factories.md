---
id: data-factories
title: Test Data Factories and Builders
category: data
priority: HIGH
triggers: [duplicated-test-payloads, wall-of-data, verbose-nested-object-creation, repetitive-mock-records]
tags: [test-data, factories, builders, faker, defaults]
---

# Test Data Factories & Builders

**Trigger Anchor:** Generate consistent test data with factory functions, fluent builders for complex configurations, and seeded faker utilities for reproducible variety.

---

## Factories with Defaults vs Inline Duplication

### Bad
```typescript
// ❌ 30-line inline object literal duplicated across every test case
test('calculates total for single item', () => {
  const order = {
    id: 'ord-1',
    customer: { id: 'c-1', email: 'c@test.com', address: { city: 'Springfield', zip: '62701' } },
    items: [{ id: 'i-1', name: 'Widget', price: 29.99, qty: 1 }],
    status: 'pending',
    createdAt: new Date()
  };
  expect(orderService.calculateTotal(order)).toBe(29.99);
});
```

### Good
```typescript
// ✅ Factory encapsulates defaults, exposing only scenario-specific overrides
const OrderFactory = {
  create(overrides: Partial<Order> = {}): Order {
    return {
      id: `ord-${Math.random().toString(36).slice(2)}`,
      customer: { id: 'c-1', email: 'c@test.com', address: { city: 'Springfield', zip: '62701' } },
      items: [{ id: 'i-1', name: 'Widget', price: 29.99, qty: 1 }],
      status: 'pending',
      createdAt: new Date(),
      ...overrides
    };
  }
};

test('calculates total for single item', () => {
  const order = OrderFactory.create({ items: [{ id: 'i-1', name: 'Book', price: 15.00, qty: 2 }] });
  expect(orderService.calculateTotal(order)).toBe(30.00);
});
```

---

## Fluent Builders & Seeded Faker for Complex Varied Data

### Bad
```typescript
// ❌ Complex configurations require fragile, deeply nested object patching
const report = { type: 'sales', filters: { regions: ['EU'] }, format: { pdf: true }, recipients: [{ email: 'ceo@test.com' }] };
```

### Good
```typescript
// ✅ Fluent builder combined with seeded faker for reproducible bulk test data
import { faker } from '@faker-js/faker';

beforeAll(() => faker.seed(42)); // Deterministic generation

class ReportBuilder {
  private report: Partial<Report> = { type: 'summary', recipients: [] };

  static create() { return new ReportBuilder(); }
  forRegion(region: string) { this.report.region = region; return this; }
  withRecipient(email = faker.internet.email()) {
    this.report.recipients!.push(email);
    return this;
  }
  build(): Report { return this.report as Report; }
}

test('builds report with regional filters', () => {
  const report = ReportBuilder.create().forRegion('EU').withRecipient().build();
  expect(report.region).toBe('EU');
  expect(report.recipients).toHaveLength(1);
});
```
