# Source explicitly to append native Git defaults to this shell's Git config.
if [ -n "${AGENT_DOTFILES_GIT_CONFIG_BASE-}" ]; then
    return 0
fi
_agent_git_count=${GIT_CONFIG_COUNT:-0}
case "$_agent_git_count" in
    ''|*[!0-9]*) printf '%s\n' 'git-env: invalid inherited GIT_CONFIG_COUNT' >&2; return 2 ;;
esac
export "GIT_CONFIG_KEY_${_agent_git_count}=core.pager"
export "GIT_CONFIG_VALUE_${_agent_git_count}=cat"
_agent_git_count=$((_agent_git_count + 1))
export "GIT_CONFIG_KEY_${_agent_git_count}=color.ui"
export "GIT_CONFIG_VALUE_${_agent_git_count}=false"
_agent_git_count=$((_agent_git_count + 1))
export "GIT_CONFIG_KEY_${_agent_git_count}=diff.algorithm"
export "GIT_CONFIG_VALUE_${_agent_git_count}=histogram"
_agent_git_count=$((_agent_git_count + 1))
export "GIT_CONFIG_KEY_${_agent_git_count}=diff.renames"
export "GIT_CONFIG_VALUE_${_agent_git_count}=true"
_agent_git_count=$((_agent_git_count + 1))
export "GIT_CONFIG_KEY_${_agent_git_count}=log.date"
export "GIT_CONFIG_VALUE_${_agent_git_count}=iso-strict"
_agent_git_count=$((_agent_git_count + 1))
export GIT_CONFIG_COUNT=$_agent_git_count
AGENT_DOTFILES_GIT_CONFIG_BASE=$(($_agent_git_count - 5))
export AGENT_DOTFILES_GIT_CONFIG_BASE
unset _agent_git_count

agent_git_deactivate() {
    local _agent_git_index=${AGENT_DOTFILES_GIT_CONFIG_BASE:-0}
    while [ "$_agent_git_index" -lt "${GIT_CONFIG_COUNT:-0}" ]; do
        unset "GIT_CONFIG_KEY_${_agent_git_index}" "GIT_CONFIG_VALUE_${_agent_git_index}"
        _agent_git_index=$((_agent_git_index + 1))
    done
    if [ "${AGENT_DOTFILES_GIT_CONFIG_BASE:-0}" -eq 0 ]; then
        unset GIT_CONFIG_COUNT
    else
        GIT_CONFIG_COUNT=$AGENT_DOTFILES_GIT_CONFIG_BASE
        export GIT_CONFIG_COUNT
    fi
    unset AGENT_DOTFILES_GIT_CONFIG_BASE AGENT_DOTFILES_SESSION_ACTIVE
    unset -f agent_git_deactivate
}
