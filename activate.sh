# One explicit Bash/Zsh entry point for the shared coding-agent session.
if [ -n "${AGENT_DOTFILES_SESSION_ACTIVE-}" ]; then
    return 0
fi

if [ -n "${BASH_VERSION-}" ]; then
    _agent_activate_source=${BASH_SOURCE[0]}
elif [ -n "${ZSH_VERSION-}" ]; then
    _agent_activate_source=${funcsourcetrace[1]%:*}
else
    printf '%s\n' 'agent-dotfiles: activate.sh must be sourced by Bash or Zsh' >&2
    return 2
fi
case "$_agent_activate_source" in
    */*) _agent_activate_parent=${_agent_activate_source%/*} ;;
    *) _agent_activate_parent=. ;;
esac
[ -n "$_agent_activate_parent" ] || _agent_activate_parent=/
_agent_activate_home=$(CDPATH='' builtin cd -- "$_agent_activate_parent" && builtin pwd -P) || return 2
unset _agent_activate_source _agent_activate_parent

for _agent_activate_file in .bashrc .zshrc git-env.sh; do
    if [ ! -r "$_agent_activate_home/$_agent_activate_file" ]; then
        printf 'agent-dotfiles: missing reviewed asset: %s\n' "$_agent_activate_file" >&2
        unset _agent_activate_file _agent_activate_home
        return 2
    fi
done
unset _agent_activate_file

if [ -n "${BASH_VERSION-}" ]; then
    # shellcheck source=.bashrc
    . "$_agent_activate_home/.bashrc" || { unset _agent_activate_home; return 2; }
else
    # shellcheck source=.zshrc
    . "$_agent_activate_home/.zshrc" || { unset _agent_activate_home; return 2; }
fi
# shellcheck source=git-env.sh
. "$_agent_activate_home/git-env.sh" || { agent_deactivate; unset _agent_activate_home; return 2; }
unset _agent_activate_home
AGENT_DOTFILES_SESSION_ACTIVE=1
