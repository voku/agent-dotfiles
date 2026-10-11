# Redpill capability profiles (S2, data-only)

The reviewed `.redpill/profiles/*.json` files are the source of truth for
`firstInstall.sh plan --profile minimal|php|debug`. The planner uses its fixed
allowlisted executable/package catalog. Files select names only; they cannot
execute commands or define arbitrary install recipes.

- `minimal`: Python 3, Git, ripgrep, jq, curl.
- `php`: inherits minimal, adds detection-only PHP and Composer.
- `debug`: inherits minimal, adds fd/fdfind, ShellCheck, hyperfine and
  Linux-only package recommendations for strace.

**This is a host bootstrap planning concern, not runtime shell activation.**
No `.redpill` file is sourced, installed into HOME, or added to the existing
private-prefix runtime installation manifest. Existing `.bashrc`, `.zshrc`,
`install.sh plan/verify/uninstall`, and published manifests remain unchanged.
No user/project-local override, plugin loader, implicit package install,
version inference, or global Git configuration is enabled.

## Evidence and failure contract

The fixed loader reads profile data relative to its own source, not `$PWD`.
It rejects malformed JSON, extra fields, wrong identity, links to external files,
unexpected inheritance, duplicate capabilities and unapproved tool names. Invalid
bundled data exits 2 with a contextual diagnostic rather than silently changing
the requested tool set. The package command is always a **proposal**, never executed.

GitHub Actions exercises the real entrypoint on all profiles using an exact-head
checkout and uploads the three JSON receipts. Python unit tests cover rejection
cases. A green run demonstrates deterministic selection and read-only planning,
**not** completed installation or any end-to-end productivity improvement.

Subsequent reviewed slices can relocate fixed shell module families beneath
`.redpill/core` while preserving the existing source/install/activation ABI.
This PR deliberately does not do that or implement optional output compression.
