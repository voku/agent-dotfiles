# Shared explicit Bash/Zsh helpers. Do not source this file directly.
if [ -z "${_agent_df_shell_dir:-}" ]; then
  printf '%s\n' 'agent-dotfiles: source shell/.bashrc or shell/.zshrc instead' >&2
  return 2
fi
_agent_df_candidate="$_agent_df_shell_dir/../bin/agent-dotfiles"
if [ ! -x "$_agent_df_candidate" ]; then
  printf '%s\n' 'agent-dotfiles: installed CLI is missing or not executable' >&2
  unset _agent_df_candidate
  return 2
fi
if [ -n "${AGENT_DOTFILES_BIN:-}" ] && [ "$AGENT_DOTFILES_BIN" != "$_agent_df_candidate" ]; then
  printf '%s\n' 'agent-dotfiles: another pinned CLI is already active; use a fresh session' >&2
  unset _agent_df_candidate
  return 2
fi
# Refuse function collisions before defining any helpers. No shell policy changes.
for _agent_df_name in agent_doctor agent_files agent_search agent_status agent_tracked agent_read agent_patch agent_history agent_blame agent_help; do
  if typeset -f "$_agent_df_name" >/dev/null 2>&1; then
    printf 'agent-dotfiles: function already defined: %s\n' "$_agent_df_name" >&2
    unset _agent_df_candidate _agent_df_name
    return 2
  fi
done
unset _agent_df_name
AGENT_DOTFILES_BIN="$_agent_df_candidate"
unset _agent_df_candidate

agent_doctor()  { "$AGENT_DOTFILES_BIN" doctor "$@"; }
agent_files()   { "$AGENT_DOTFILES_BIN" files "$@"; }
agent_search()  { "$AGENT_DOTFILES_BIN" search "$@"; }
agent_status()  { "$AGENT_DOTFILES_BIN" git-status "$@"; }
agent_tracked() { "$AGENT_DOTFILES_BIN" tracked "$@"; }
agent_read()    { "$AGENT_DOTFILES_BIN" read "$@"; }
agent_patch()   { "$AGENT_DOTFILES_BIN" git-patch "$@"; }

# History and blame must remain native Git operations: no reduced/rewritten evidence.
agent_history() {
  if [ "$#" -gt 1 ]; then
    printf '%s\n' 'agent_history: usage: agent_history [count 1..1000]' >&2
    return 2
  fi
  case "${1:-10}" in
    *[!0-9]*|'') printf '%s\n' 'agent_history: count must be an integer' >&2; return 2 ;;
  esac
  if [ "${1:-10}" -lt 1 ] || [ "${1:-10}" -gt 1000 ]; then
    printf '%s\n' 'agent_history: count must be within 1..1000' >&2
    return 2
  fi
  command git --no-pager log --format=fuller -n "${1:-10}"
}

agent_blame() {
  if [ "$#" -ne 3 ]; then
    printf '%s\n' 'agent_blame: usage: agent_blame PATH START END' >&2
    return 2
  fi
  case "$2:$3" in
    *[!0-9:]*|:|:*|*:) printf '%s\n' 'agent_blame: invalid line numbers' >&2; return 2 ;;
  esac
  if [ "$2" -lt 1 ] || [ "$3" -lt "$2" ]; then
    printf '%s\n' 'agent_blame: invalid line interval' >&2
    return 2
  fi
  command git --no-pager blame --line-porcelain -L "$2,$3" -- "$1"
}

agent_help() {
  printf '%s\n' 'agent_doctor/files/search/status/tracked/read/patch: exact JSON from pinned CLI' \
    'agent_history [count]: native Git full commit metadata (1..1000)' \
    'agent_blame PATH START END: native Git line porcelain' \
    'No aliases, hooks, PATH changes, global configuration or automatic activation.'
}
