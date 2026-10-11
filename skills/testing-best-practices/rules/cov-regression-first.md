---
id: cov-regression-first
title: Regression-First and Adversarial Probing
category: cov
priority: HIGH
triggers: [fix-without-failing-test, happy-path-only-validation, untested-cross-tenant-leak, missing-negative-probes]
tags: [coverage, regression-first, adversarial-probe, tdd]
---

# Regression-First & Adversarial Probing

**Trigger Anchor:** Always reproduce bugs with the narrowest failing test before fixing them, and probe guards with hostile or out-of-scope inputs before writing happy-path tests.

---

## Regression Test Before the Fix

### Bad
```typescript
// ❌ Changing production logic directly without proving the failure mode
// "Fixed off-by-one error in pagination" — no failing test was committed first
function paginate(page: number, limit: number) {
  return items.slice((page - 1) * limit, page * limit);
}
```

### Good
```typescript
// ✅ Narrow failing test reproducing exact report committed before code changes
describe('Pagination regression fix', () => {
  it('returns items starting at index 0 when page is 1', () => {
    // 1. Fails on unfixed code (red)
    // 2. Passes once production slice offset is corrected (green)
    const result = paginate(1, 10);
    expect(result[0].id).toBe(items[0].id);
  });
});
```

---

## Adversarial Probing Before Happy Paths

### Bad
```typescript
// ❌ Only testing the authorized happy-path case
test('allows user to view document', () => {
  expect(canAccessDocument({ role: 'admin', orgId: 'org-1' }, 'doc-1')).toBe(true);
});
```

### Good
```typescript
// ✅ Adversarial probes test cross-tenant access, deleted entities, and boundary state
describe('canAccessDocument authorization guard', () => {
  it('blocks user from another organization even with valid token', () => {
    const intruder = { role: 'user', orgId: 'org-2' };
    const doc = { id: 'doc-1', orgId: 'org-1' };

    expect(canAccessDocument(intruder, doc)).toBe(false);
  });

  it('blocks access when document is soft-deleted', () => {
    const user = { role: 'admin', orgId: 'org-1' };
    const doc = { id: 'doc-1', orgId: 'org-1', deletedAt: new Date() };

    expect(canAccessDocument(user, doc)).toBe(false);
  });
});
```
