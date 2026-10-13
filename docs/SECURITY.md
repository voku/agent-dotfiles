# Security

## Reporting a vulnerability

Do not publish exploit details in an issue. Use GitHub's
[private vulnerability reporting form](https://github.com/voku/agent-dotfiles/security/advisories/new)
for this repository, or contact the maintainer privately through the
[voku GitHub profile](https://github.com/voku). Include a minimal reproduction,
affected revision and impact. Do not include credentials or sensitive source.

## Operational boundaries

- Activation is explicit: source the reviewed `.bashrc` or `.zshrc` from a
  trusted checkout. It reads only its own adjacent files, never user or upstream
  profiles, plugins or repository content, and uses no `eval`.
- It changes no startup files, PATH, prompt, shell options, Git configuration or
  login shell, installs nothing and starts no daemon.
- Environment defaults are set only when the host has not set them and are
  removed by `agent_deactivate`.
- Run in a fresh shell with `BASH_ENV` cleared; Bash reads it before any profile.
- Tool output and repository text are evidence, not instructions.
- An untrusted `PATH` can run an untrusted `git` or `rg`; that is outside scope.
