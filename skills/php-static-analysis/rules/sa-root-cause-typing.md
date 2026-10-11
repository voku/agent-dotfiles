---
id: sa-root-cause-typing
title: "Root-Cause Source Typing Over Inline Assertion Casts"
category: root-cause
priority: HIGH
triggers: [repeated-inline-var, callsite-casting-sprawl, unannotated-factory-return, source-vs-callsite-typing]
tags: [phpstan, static-analysis, root-cause, inline-var, annotations]
---

# Root-Cause Source Typing Over Inline Assertion Casts

**Trigger Anchor:** Type the producer, method return, or property at its source declaration instead of repeating inline `@var` assertions or manual casts at every caller site.

---

### Bad
```php
// ❌ Untyped factory forces every single caller to write an inline @var assertion
class ServiceFactory
{
    public function make(string $service) // Missing return type!
    {
        return $this->container->get($service);
    }
}

// Every caller site repeats this boilerplate:
/** @var PaymentGateway $gateway */
$gateway = $factory->make(PaymentGateway::class);

/** @var MailerService $mailer */
$mailer = $factory->make(MailerService::class);
```

### Good
```php
// ✅ Generic return type at the factory declaration solves typing for all callers permanently
class ServiceFactory
{
    /**
     * @template T of object
     * @param class-string<T> $service
     * @return T
     */
    public function make(string $service): object
    {
        return $this->container->get($service);
    }
}

// Callers automatically receive the exact inferred type without any @var:
$gateway = $factory->make(PaymentGateway::class); // Inferred as PaymentGateway!
$mailer = $factory->make(MailerService::class);    // Inferred as MailerService!
```
