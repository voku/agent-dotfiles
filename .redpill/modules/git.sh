# Native read-only Git provenance helpers. No global Git configuration.
agent_history() { agent_git --literal-pathspecs log "$@"; }
agent_blame() { agent_git --literal-pathspecs blame --line-porcelain "$@"; }
