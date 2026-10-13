# Remove exactly the public agent-owned namespace; do not restore host state.
agent_deactivate() {
    if typeset -f agent_git_deactivate >/dev/null 2>&1; then
        agent_git_deactivate || return $?
    fi
    unset AGENT_DOTFILES_HOME
    unset AGENT_DOTFILES_SESSION_ACTIVE
    unset -f agent_deactivate agent_context agent_root agent_diff agent_diff_check agent_mkcd
}
