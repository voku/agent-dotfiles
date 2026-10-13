# Reviewed, fixed asset preflight: never discover or execute host plugins.
_agent_dotfiles_activate() {
    local _agent_home="$1" _agent_name
    for _agent_name in .exports .functions .aliases .redpill/core/deactivation.sh .redpill/modules/context.sh .redpill/modules/git.sh; do
        if [ ! -f "$_agent_home/$_agent_name" ] || [ ! -r "$_agent_home/$_agent_name" ]; then
            printf 'agent-dotfiles: required %s is missing or unreadable\n' "$_agent_name" >&2
            return 2
        fi
    done
    if [ "${AGENT_DOTFILES_HOME+x}" = x ]; then
        printf 'agent-dotfiles: AGENT_DOTFILES_HOME already exists; deactivate first\n' >&2
        return 2
    fi
    for _agent_name in agent_deactivate agent_git_deactivate agent_context agent_root agent_diff agent_diff_check agent_mkcd; do
        if typeset -f "$_agent_name" >/dev/null 2>&1 || alias "$_agent_name" >/dev/null 2>&1; then
            printf 'agent-dotfiles: owned namespace collision: %s\n' "$_agent_name" >&2
            return 2
        fi
    done
    # Preserve the original exports and explicit module order.
    . "$_agent_home/.exports" "$_agent_home"
    # shellcheck source=../../.functions
    . "$_agent_home/.functions"
}
