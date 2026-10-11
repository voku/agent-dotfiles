---
id: iso-cleanup
title: Test Resource and Side-Effect Cleanup
category: iso
priority: CRITICAL
triggers: [leaked-temp-files, open-db-connections, lingering-http-servers, polluted-env-vars, dangling-event-listeners]
tags: [test-isolation, cleanup, resource-management, side-effects]
---

# Test Resource & Side-Effect Cleanup

**Trigger Anchor:** Clean up all disk files, database mutations, network listeners, global environment variables, and event handlers after every test.

---

### Bad
```typescript
// ❌ Side effects mutate global environment and disk without teardown
describe('Config & File Processor', () => {
  test('modifies environment and writes scratch file', async () => {
    process.env.API_KEY = 'temporary-test-key';
    await fs.writeFile('/tmp/test-out.json', '{"status":"ok"}');
    window.addEventListener('resize', onResize);
    // Leaks: API_KEY stays set, /tmp file lingers, event listener triggers in later suites
  });
});
```

### Good
```typescript
// ✅ Explicit reset of environment, listeners, and filesystem in teardown
describe('Config & File Processor', () => {
  const originalEnv = { ...process.env };
  const trackedFiles: string[] = [];

  afterEach(async () => {
    process.env = { ...originalEnv };
    window.removeEventListener('resize', onResize);
    await Promise.all(trackedFiles.map(file => fs.rm(file, { force: true })));
    trackedFiles.length = 0;
  });

  test('modifies environment and writes scratch file cleanly', async () => {
    process.env.API_KEY = 'temporary-test-key';
    const filePath = '/tmp/test-out.json';
    trackedFiles.push(filePath);

    await fs.writeFile(filePath, '{"status":"ok"}');
    expect(loadConfig().apiKey).toBe('temporary-test-key');
  });
});
```
