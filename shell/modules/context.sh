# Machine-output source helpers. Fixed reviewed module, no global aliases.
agent_dotfiles() { PYTHONDONTWRITEBYTECODE=1 command "$AGENT_DOTFILES_HOME/bin/agent-dotfiles" "$@"; }
agent_doctor() { agent_dotfiles doctor "$@"; }
agent_workspace() { agent_dotfiles workspace "$@"; }
agent_files() { agent_dotfiles files "$@"; }
agent_search() { agent_dotfiles search "$@"; }
agent_read() { agent_dotfiles read "$@"; }
agent_tracked() { agent_dotfiles tracked "$@"; }
agent_status() { agent_dotfiles git-status "$@"; }
agent_patch() { agent_dotfiles git-patch "$@"; }
