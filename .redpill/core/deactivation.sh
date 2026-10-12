# Remove exactly the public agent-owned namespace; do not restore host state.
agent_deactivate() {
    unset AGENT_DOTFILES_HOME
    unset -f agent_dotfiles agent_doctor agent_workspace agent_files agent_search agent_read agent_tracked agent_status agent_patch agent_history agent_blame agent_git agent_rg agent_deactivate
}
