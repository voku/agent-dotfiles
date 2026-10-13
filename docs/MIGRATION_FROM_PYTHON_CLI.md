# Migration from the Python consumer CLI

The Python commands for repository search, source ranges and Git patches have
been removed. Coding agents can use the project's native tools directly:

```sh
git status --short --branch
rg -n --hidden --glob '!vendor/**' 'symbol' src tests
sed -n '40,100p' src/path/to/file.php
git diff -- src/path/to/file.php
```

These commands retain native output, errors and exit codes. Use `agent_context`
for a compact repository orientation; it reports Composer metadata and
available checks when the repository has a root `composer.json`. It does not
run project scripts. Continue using project-defined Composer scripts and test
commands as documented by each repository.

Python remains an internal implementation detail for the pinned installer and
maintainer tooling. It is not a required daily command language for consumers.
