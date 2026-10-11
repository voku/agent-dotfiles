# Source this reviewed profile explicitly in a fresh Zsh shell.
if [ -z "${ZSH_VERSION-}" ]; then
    printf 'agent-dotfiles: .zshrc requires Zsh\n' >&2
    return 2
fi
# Explicit agent-owned zsh entry point; never loads user profiles.
_agent_dotfiles_source_profile() {
    local _agent_source="${funcsourcetrace[1]%:*}" _agent_parent _agent_home _agent_status
    case "$_agent_source" in
        */*) _agent_parent=${_agent_source%/*} ;;
        *) _agent_parent=. ;;
    esac
    [ -n "$_agent_parent" ] || _agent_parent=/
    _agent_home=$(CDPATH='' builtin cd -- "$_agent_parent" && builtin pwd -P && printf '.') || {
        unset -f _agent_dotfiles_source_profile
        return 2
    }
    _agent_home=${_agent_home%.}
    _agent_home=${_agent_home%$'\n'}
    if [ ! -r "$_agent_home/.shellrc" ]; then
        printf 'agent-dotfiles: required .shellrc is missing or unreadable\n' >&2
        unset -f _agent_dotfiles_source_profile
        return 2
    fi
    . "$_agent_home/.shellrc"
    _agent_status=$?
    unset -f _agent_dotfiles_source_profile
    return "$_agent_status"
}
_agent_dotfiles_source_profile
