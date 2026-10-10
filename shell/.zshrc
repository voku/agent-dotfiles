# agent-dotfiles: explicitly source this file; never add to a user's startup files.
if [ -z "${ZSH_VERSION:-}" ]; then
  printf '%s\n' 'agent-dotfiles: Zsh required' >&2
  return 2
fi
_agent_df_shell_file="${(%):-%N}"
_agent_df_shell_dir="$(cd -P -- "${_agent_df_shell_file:h}" && pwd -P)" || return 2
. "$_agent_df_shell_dir/agent-functions.sh"
_agent_df_status=$?
unset _agent_df_shell_file _agent_df_shell_dir
return "$_agent_df_status"
