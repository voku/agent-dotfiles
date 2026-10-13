# Source explicitly to append native Git defaults to this shell's Git config.
if [ -n "${AGENT_DOTFILES_GIT_CONFIG_BASE-}" ]; then
    return 0
fi
_agent_git_start=${GIT_CONFIG_COUNT:-0}
case "$_agent_git_start" in
    ''|*[!0-9]*) printf '%s\n' 'git-env: invalid inherited GIT_CONFIG_COUNT' >&2; return 2 ;;
esac
export "GIT_CONFIG_KEY_${_agent_git_start}=core.pager"
export "GIT_CONFIG_VALUE_${_agent_git_start}=cat"
_agent_git_index=$((_agent_git_start + 1))
export "GIT_CONFIG_KEY_${_agent_git_index}=color.ui"
export "GIT_CONFIG_VALUE_${_agent_git_index}=false"
_agent_git_index=$((_agent_git_index + 1))
export "GIT_CONFIG_KEY_${_agent_git_index}=diff.algorithm"
export "GIT_CONFIG_VALUE_${_agent_git_index}=histogram"
_agent_git_index=$((_agent_git_index + 1))
export "GIT_CONFIG_KEY_${_agent_git_index}=diff.renames"
export "GIT_CONFIG_VALUE_${_agent_git_index}=true"
_agent_git_index=$((_agent_git_index + 1))
export "GIT_CONFIG_KEY_${_agent_git_index}=log.date"
export "GIT_CONFIG_VALUE_${_agent_git_index}=iso-strict"
_agent_git_end=$((_agent_git_index + 1))
export GIT_CONFIG_COUNT=$_agent_git_end
AGENT_DOTFILES_GIT_CONFIG_BASE=$_agent_git_start
AGENT_DOTFILES_GIT_CONFIG_END=$_agent_git_end
export AGENT_DOTFILES_GIT_CONFIG_BASE AGENT_DOTFILES_GIT_CONFIG_END
unset _agent_git_start _agent_git_index _agent_git_end

agent_git_deactivate() {
    local _agent_git_start=${AGENT_DOTFILES_GIT_CONFIG_BASE:-0}
    local _agent_git_end=${AGENT_DOTFILES_GIT_CONFIG_END:-0}
    local _agent_git_index _agent_git_offset _agent_git_expected_key _agent_git_expected_value
    local _agent_git_actual_key _agent_git_actual_value
    case "$_agent_git_start:$_agent_git_end:${GIT_CONFIG_COUNT:-0}" in
        *[!0-9:]*) printf '%s\n' 'git-env: refusing to restore invalid Git config slot metadata' >&2; return 2 ;;
    esac
    if [ "$_agent_git_end" -ne "$((_agent_git_start + 5))" ] \
        || [ "${GIT_CONFIG_COUNT:-0}" -ne "$_agent_git_end" ]; then
        printf '%s\n' 'git-env: refusing to restore; Git config slots changed after activation' >&2
        return 2
    fi
    _agent_git_index=$_agent_git_start
    while [ "$_agent_git_index" -lt "$_agent_git_end" ]; do
        _agent_git_offset=$((_agent_git_index - _agent_git_start))
        case "$_agent_git_offset" in
            0) _agent_git_expected_key=core.pager; _agent_git_expected_value=cat ;;
            1) _agent_git_expected_key=color.ui; _agent_git_expected_value=false ;;
            2) _agent_git_expected_key=diff.algorithm; _agent_git_expected_value=histogram ;;
            3) _agent_git_expected_key=diff.renames; _agent_git_expected_value=true ;;
            4) _agent_git_expected_key=log.date; _agent_git_expected_value=iso-strict ;;
        esac
        # The dynamic suffix contains only the validated decimal index above.
        eval "_agent_git_actual_key=\${GIT_CONFIG_KEY_${_agent_git_index}-}"
        eval "_agent_git_actual_value=\${GIT_CONFIG_VALUE_${_agent_git_index}-}"
        if [ "$_agent_git_actual_key" != "$_agent_git_expected_key" ] \
            || [ "$_agent_git_actual_value" != "$_agent_git_expected_value" ]; then
            printf '%s\n' 'git-env: refusing to restore; an owned Git config slot was changed' >&2
            return 2
        fi
        _agent_git_index=$((_agent_git_index + 1))
    done
    _agent_git_index=$_agent_git_start
    while [ "$_agent_git_index" -lt "$_agent_git_end" ]; do
        unset "GIT_CONFIG_KEY_${_agent_git_index}" "GIT_CONFIG_VALUE_${_agent_git_index}"
        _agent_git_index=$((_agent_git_index + 1))
    done
    if [ "$_agent_git_start" -eq 0 ]; then
        unset GIT_CONFIG_COUNT
    else
        GIT_CONFIG_COUNT=$_agent_git_start
        export GIT_CONFIG_COUNT
    fi
    unset AGENT_DOTFILES_GIT_CONFIG_BASE AGENT_DOTFILES_GIT_CONFIG_END AGENT_DOTFILES_SESSION_ACTIVE
    unset -f agent_git_deactivate
}
