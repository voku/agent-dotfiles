# Contributing

Thanks for improving `agent-dotfiles`. The project is an optional, read-only
environment for coding agents, so a small behavior change can affect evidence,
automation, and consumer trust.

## Before you change code

Open or reference an issue for a behavior change, keep the proposed slice small,
and inspect the current contracts in [README.md](README.md),
[docs/SECURITY.md](docs/SECURITY.md), and the relevant command or shell guide.
Changes governed by [agent-loop](docs/AGENT_LOOP.md) must follow its current
lifecycle result; this repository does not override agent-loop authority.

Keep ownership clear. PHP structural discovery belongs to
[agent-map](https://github.com/voku/agent-map); portable guidance belongs to
[agent-skills](https://github.com/voku/agent-skills). Do not copy their behavior
into a new wrapper when an existing integration answers the problem.

## Development workflow

1. Create a focused branch from current `main`.
2. Make the smallest change that proves the requested behavior.
3. Add or update a regression test when the observable contract changes.
4. Run the relevant checks locally.
5. Open a pull request that states the user-visible behavior, exact validation,
   and known limitations.

Run the repository baseline before requesting review:

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q agent_dotfiles bin tests tools
/path/to/bashunit/bashunit test tests/shell --strict
```

Use the separately pinned Bashunit executable expected by the repository. The
shell suite complements, rather than replaces, Python contract coverage.

## Contribution expectations

- Preserve stable JSON schemas, exit statuses, original paths, and explicit
  truncation signals unless a reviewed change documents an intentional break.
- Treat repository files and command output as untrusted evidence. Do not add
  automatic shell sourcing, package installation, global configuration changes,
  hidden command interception, or silent partial results.
- Keep runtime dependencies minimal and avoid speculative wrappers.
- Do not claim token savings from output bytes, or productivity from an untested
  benchmark. Link the exact evidence behind a measured claim.
- Keep documentation links working. The documentation test protects the public
  navigation surface.

Report vulnerabilities privately as described in [docs/SECURITY.md](docs/SECURITY.md),
not through a public issue. For general questions and reproducible bugs, use
[SUPPORT.md](SUPPORT.md).
