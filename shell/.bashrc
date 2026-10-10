# agent-dotfiles: explicitly source this file; never add to a user's startup files.
if [ -z "${BASH_VERSION:-}" ]; then
  printf '%s\n' 'agent-dotfiles: Bash required' >&2
  return 2
fi
_agent_df_shell_dir="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)" || return 2
# shellcheck source=agent-functions.sh
. "$_agent_df_shell_dir/agent-functions.sh"
_agent_df_status=$?
unset _agent_df_shell_dir
return "$_agent_df_status"
