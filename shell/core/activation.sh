# Reviewed, fixed asset preflight: never discover or execute host plugins.
_agent_dotfiles_activate() {
    local _agent_home="$1" _agent_name
    for _agent_name in .exports .functions shell/core/deactivation.sh shell/modules/context.sh shell/modules/git.sh; do
        if [ ! -f "$_agent_home/$_agent_name" ] || [ ! -r "$_agent_home/$_agent_name" ]; then
            printf 'agent-dotfiles: required %s is missing or unreadable\n' "$_agent_name" >&2
            return 2
        fi
    done
    if [ ! -f "$_agent_home/bin/agent-dotfiles" ] || [ ! -x "$_agent_home/bin/agent-dotfiles" ]; then
        printf 'agent-dotfiles: required bin/agent-dotfiles is missing or not executable\n' >&2
        return 2
    fi
    if [ "${AGENT_DOTFILES_HOME+x}" = x ]; then
        printf 'agent-dotfiles: AGENT_DOTFILES_HOME already exists; deactivate first\n' >&2
        return 2
    fi
    for _agent_name in agent_dotfiles agent_doctor agent_files agent_search agent_read agent_tracked agent_status agent_patch agent_history agent_blame agent_deactivate; do
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
