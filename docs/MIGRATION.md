# Migration from voku/dotfiles

Files are migrated one at a time, small and generic first. A file is **adapted**
(content kept, tuned for agents), **skipped** (with the reason) or **deferred**
(too big for round one). Interactive, prompt, color and history material is
skipped by design: it is for a human at a terminal.

## Round 1: small, generic files

| Source | Result | Where / why |
| --- | --- | --- |
| `.gitignore_global`, `.global_gitignore` | Adapted | Merged into `.redpill/config/gitignore_global`; editor/OS noise only. Archives, logs, `*.sqlite`, binaries and `tags` dropped: an agent may need to see them |
| `.curlrc` | Adapted | `agent_curl` in `.functions`; `progress-bar` became `--silent --show-error`, redirects kept. The UA spoof and `connect-timeout` were not carried over |
| `.exports` (small parts) | Adapted | `PYTHONIOENCODING`, pager and color variables are in `.redpill/config/agent.env`; the rest is deferred |
| `.editorconfig` | Already present | This repo's own rules differ (4 spaces); not replaced |
| `.gitignore` (gitignore.io) | Skipped | Project ignore list, duplicated by the global file |
| `.gitmessage` | Skipped | Commit templates only show in an editor; agents use `-m` and must follow the target repo's convention. Jira/time-tracking hints are personal |
| `.git-templates/hooks/post-checkout` | Skipped | Writes `~/.git-clone-init` and local Git identity: host mutation |
| `.gitattributes` | Skipped | Only commented-out content |
| `.wgetrc` | Deferred (single tool) | Skipped in round 1. Later: keep `timeout`, `tries`, `retry_connrefused`, `no_parent`, `server_response`; drop the IE user-agent, `robots = off`, `follow_ftp`. Applying it needs `WGETRC`, which would hide a user's own `~/.wgetrc`, so it stays opt-in |
| `.ackrc`, `.colordiffrc`, `.gemrc`, `.irbrc`, `.gdbinit`, `.screenrc`, `.tmux.conf`, `.minttyrc`, `.gvimrc`, `.xbindkeysrc`, `.hgignore` (Mercurial duplicate of the global ignore) | Skipped | One tool each; not needed by an agent shell |
| `.hushlogin`, `.inputrc`, `.bash_logout`, `.bash_complete`, `.colors`, `.dircolors`, `.icons`, `.fonts/`, `.vim*` | Skipped | Login, readline, completion, color and editor concerns for humans |
| `.zprofile`, `.bash_profile`, `.zshrc`, `.bashrc`, `.shellrc` (source) | Skipped / replaced | Login/interactive startup that loads `~/.extra`, prompt, plugins and themes. This repo has its own explicit entry points |
| `.travis.yml`, `.osx` | Skipped | Dead CI config for the old test suite; `.osx` is a one-line pointer to `.macos` |
| `.load`, `.dotfilecheck`, `.IGNORE`, `.config_dotfiles_default`, `bootstrap.sh`, `firstInstall*.sh` | Skipped | Installer and host-mutation machinery; this repo has none by design |

## Round 2: `.redpill/`

The framework is interactive (themes, prompts, completion, key bindings,
history, 266 zsh and 68 bash plugins, mostly aliases) and its tools install,
upgrade or uninstall the framework itself. Two pieces were worth adapting.

| Source | Result | Where / why |
| --- | --- | --- |
| `tools/require_tool.sh` | Adapted | `agent_require`: distinct exit codes for missing / too old / unreadable. The awk version compare became `sort -V`; the `$TOOL` environment override was dropped (it executed whatever the variable held). Replaces the removed `doctor` |
| `plugins/available/base.plugin.bash` `usage`, `command_exists` | Adapted | `agent_usage` (`du -h -d 1`); `command_exists` is covered by `agent_require` |
| `plugins/available/extract.plugin.bash` | Adapted in round 3 | `gunzip`/`xz`/`uncompress` deleted the archive and unpacked into the cwd; `agent_extract` requires a destination and keeps the archive |
| `lib/git.zsh`, `plugins/git`, `composer`, `docker*`, `npm`-style aliases | Skipped | Prompt segments and interactive aliases; native `agent_git` covers the evidence |
| `lib/3_functions.zsh` (`take`, `open_command`, ...) | Skipped | Change cwd or open GUI programs |
| `lib/*.bash`, `lib/*.zsh` (composure, preexec, options, completion, history, key-bindings, termsupport, spectrum) | Skipped | Prompt hooks, readline and terminal control |
| `tools/{install,uninstall,upgrade,check_for_upgrade,theme_chooser}.sh`, `redpill-init-*.sh` | Skipped | Framework lifecycle and host mutation; replaced by `.shellrc` and `.redpill/lib/` |
| `aliases/`, `bash_prompt/`, `zsh_prompt/`, `themes/`, `completion/` | Skipped | Human interface |
| `plugins/available/{ips,myip,down4me,explain,proxy,aws,...}` | Skipped | Network calls to third-party services or credentials |
| `plugins/available/{mkcd,quiet,banish-cookies,passgen,pmdown}`, `pyedit`, `shttp` | Skipped | Change cwd, background jobs, rewrite `~`, or open an editor |

Also new, prompted by a silently truncated `ls | head -80` during round 1:
`agent_head`, a `head` that always says how much it left out.

## Round 3: `bin/`, `.functions`, `.exports`

The original functions were written for a human typing at a prompt and several
are broken (`netstat_free_local_port` never checks its candidates, `replace`
quotes its variables wrongly, `command_exists` returns the wrong value). Useful
ideas were rewritten rather than copied.

| Source | Result | Where / why |
| --- | --- | --- |
| `os-info()`, `bin/os-detect.sh`, `cpuinfo()` | Adapted | `agent_os`: `key=value`, reads `/etc/os-release`, adds WSL; no `lsb_release`, no bash-4 `declare -A` |
| `netstat_used_local_ports`, `netstat_free_local_port` | Adapted | `agent_ports`, `agent_free_port` (`ss`, else `netstat`) |
| `json()` | Adapted | `agent_json`: no `pygmentize` color; uses `jq` or `json.tool` |
| `escape`, `unidecode`, `codepoint` | Adapted | `agent_codepoints`: reveals invisible characters instead of converting escapes |
| `php-parse-error-check()` | Adapted | `agent_php_lint`: reports counts and the skipped directories instead of grepping for one message |
| `extract()` | Adapted | `agent_extract` with an explicit destination (see round 2) |
| `duh`, `fs`, `ff`, `fstr`, `gz`, `calc`, `psgrep`, `tre` | Skipped | Native `du`, `find`, `rg`, `pgrep`, `python3` do it, or they page/color (`more`, `less`, `tree -C`) |
| `pidenv`, `processenv` | Skipped | Dump another process's environment, which commonly holds secrets |
| `stripspace`, `replace`, `file_backup*`, `mkd`, `mkf`, `cleanTheSystem`, `iptablesBlockIP`, `logssh`, `sshkey`, `banish-cookies` | Skipped | Rewrite files, the system or SSH state; need an explicit approval path, not a shell default |
| `cd`, `man`, `lman`, `m`, `s`, `a`, `v`, `o`, `t`, `note*`, `battery_*`, `prompt_callback`, `__git_prompt`, `__svn_branch`, `print_all_colors`, `history_top_used` | Skipped | Overrides of native commands, interactive UI or prompts |
| `testConnection`, `sniff`, `httpdump`, `httpDebug`, `digga`, `getcertnames`, `gitio`, `shorturl`, `server`, `phpserver`, `wtfis`, `whenis` | Skipped | Network or listening services; add case by case with the endpoint named |
| `bin/gitstatus*`, `bin/git-branch-status`, `bin/diff-highlight` | Skipped | Prompt segments and colored output |
| `bin/git-remove-merged-branches.sh` | Skipped | Deletes branches (including the default one) without confirmation |
| `bin/burl`, `httpcompression`, `speedtest_cli.py`, `pinhole.py`, `browser-optimizer.sh`, `img-min.sh`, `matrix.sh`, `gov.sh`, `mysql_rename_database.sh`, `du-ext.pl` | Skipped | Single-purpose tools, network, or host changes |
| `.aliases` (110 aliases) | Skipped | Aliases do not expand in non-interactive shells; the useful ones (`g`, `ll`, `..`) are native commands or `cd` shortcuts |
| `.exports`: locale detection, `IS_TTY`, `LESS`, `HIST*`, Java/Android/Ruby/Node paths | Skipped | Locale/`PATH` changes alter behavior for the whole session; history and pager variables are for humans. `PYTHONIOENCODING` kept |

## Round 4: remaining files

| Source | Result | Where / why |
| --- | --- | --- |
| `.gitconfig` (aliases, color, pager, url rewrites, credential cache, rerere, rebase, hub) | Skipped | Global Git configuration is the user's, and color/pager/`diff-highlight`/`credential.helper=cache`/`rebase.autoStash`/`rerere` change behavior or hide state. Only idea worth keeping, for your own `~/.gitconfig`: `merge.conflictstyle = zdiff3` (Git 2.35+; `diff3` before) shows the common ancestor in conflict markers, which helps an agent resolve conflicts. `agent_git` stays native and sets only `color.ui=false` per command |
| `.config/fontconfig`, `.macos`, `.osx`, `examples/` (Android SDK installer, Sublime settings, vim cheatsheet, screenshot) | Skipped | Desktop, macOS defaults and installers |
| `docs/` (CONFIGURATION, PLUGINS, RECIPES, TECHNICAL_DOCUMENTATION) | Skipped | Documentation of the human framework |
| `.redpill/tests/functions-tests.sh` | Superseded | Tested `lc`/`uc` with shunit2; replaced by `tests/shell/activation_test.sh` (Bashunit) |
| `.wgetrc` | Deferred | See round 1; opt-in only because wget has no non-intrusive way to load it |

Everything in the source repository has now been reviewed once. New candidates
come from real agent tasks that needed something and lacked it, not from
carrying more files over.

## Deferred

(none; see round 3 and 4). Add helpers only when a real task needs one: pure,
non-interactive, no aliases, prompts or `cd` override. Git config ideas must
become per-command options or opt-in files, never edits to global Git
configuration.
