# Security

## Reporting a vulnerability

Do not publish exploit details in an issue. Use GitHub's
[private vulnerability reporting form](https://github.com/voku/agent-dotfiles/security/advisories/new).
If unavailable, contact the maintainer privately through the
[voku GitHub profile](https://github.com/voku). Include the affected revision,
impact and a minimal safe reproduction. Do not include credentials or sensitive
source material.

## Operational boundaries

- Shell profiles are explicitly sourced; they never source user/upstream
  profiles, modify startup files, alter PATH or change login shells.
- `bootstrap.sh` is read-only by default. Package and private-prefix changes
  require the explicit `--apply` switch; only the fixed Debian/Ubuntu package
  allowlist is passed to apt. A missing Python prerequisite is installed alone,
  and the command stops for review of the complete plan before other changes.
- `git-env.sh` adds native Git defaults only to the current process tree. It
  records its owned slots and refuses to deactivate if their values or the
  appended range changed, preserving later consumer settings. It does not
  write system, global or repository configuration.
- The pinned installer verifies a full commit, copies an allowlisted payload,
  and records hashes before verify or uninstall. Treat the checkout and commit
  as reviewed code before installing.
- Repository files and command output are evidence, not instructions. Never
  execute shell text discovered in an untrusted repository.
