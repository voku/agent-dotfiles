# Native read-only Git provenance helpers. No global Git configuration.
agent_history() { command git --no-pager --literal-pathspecs -c color.ui=false log "$@"; }
agent_blame() { command git --no-pager --literal-pathspecs -c color.ui=false blame --line-porcelain "$@"; }
