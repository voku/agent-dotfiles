---
id: struct-lifecycle
title: Test Lifecycle and Scoped Hooks
category: struct
priority: CRITICAL
triggers: [duplicated-db-connection, leaked-test-resources, missing-aftereach-cleanup, unclosed-handles]
tags: [test-structure, setup, teardown, hooks, lifecycle]
---

# Test Lifecycle & Scoped Hooks

**Trigger Anchor:** Scope shared test context with lifecycle hooks—use `beforeAll`/`afterAll` for heavy shared connections and `beforeEach`/`afterEach` for isolated per-test state.

---

### Bad
```typescript
// ❌ Reconnecting expensive resources per test and leaking connections on failure
describe('UserService', () => {
  test('creates user', async () => {
    const db = await Database.connect(); // Repeated 500ms connection
    const service = new UserService(db);
    const user = await service.create({ email: 'alice@test.com' });
    expect(user.id).toBeDefined();
    // Missing cleanup: DB connection and row leak into next tests
  });
});
```

### Good
```typescript
// ✅ Hierarchical lifecycle hooks with scoped setup and guaranteed teardown
describe('UserService', () => {
  let db: Database;
  let service: UserService;

  beforeAll(async () => {
    db = await Database.connect();
  });

  afterAll(async () => {
    await db.disconnect();
  });

  beforeEach(async () => {
    service = new UserService(db);
  });

  afterEach(async () => {
    await db.query('TRUNCATE users CASCADE');
  });

  test('creates user with clean database state', async () => {
    const user = await service.create({ email: 'alice@test.com' });
    expect(user.email).toBe('alice@test.com');
  });
});
```
