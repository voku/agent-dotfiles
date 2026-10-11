#!/usr/bin/env python3
"""Read-only capability plan for agent-dotfiles developer tools (Python 3.10+)."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import platform
import shutil
from typing import Literal

# Bundled, reviewed profile data. Direct execution and package imports are both supported.
if __package__:
    from .profile_catalog import resolve_profile
else:
    from profile_catalog import resolve_profile


Profile = Literal["minimal", "php", "debug"]


@dataclass(frozen=True, slots=True)
class Tool:
    name: str
    commands: tuple[str, ...]
    category: str
    apt: str | None
    brew: str | None


COMMON: tuple[Tool, ...] = (
    Tool("python3", ("python3",), "runtime", "python3", "python"),
    Tool("git", ("git",), "version-control", "git", "git"),
    Tool("rg", ("rg",), "search", "ripgrep", "ripgrep"),
    Tool("jq", ("jq",), "structured-output", "jq", "jq"),
    Tool("curl", ("curl",), "http-opt-in", "curl", "curl"),
)
PHP: tuple[Tool, ...] = (
    Tool("php", ("php",), "project-dependent", None, None),
    Tool("composer", ("composer",), "project-dependent", None, None),
)
DEBUG: tuple[Tool, ...] = (
    Tool("fd", ("fd", "fdfind"), "file-navigation", "fd-find", "fd"),
    Tool("shellcheck", ("shellcheck",), "shell-validation", "shellcheck", "shellcheck"),
    Tool("hyperfine", ("hyperfine",), "benchmarking", "hyperfine", "hyperfine"),
    Tool("strace", ("strace",), "linux-diagnostics", "strace", None),
)


def package_manager(system: str, os_release: dict[str, str], has_brew: bool, has_apt: bool) -> str | None:
    """Only return package managers whose OS family and executable are confirmed."""
    if system == "Darwin":
        return "brew" if has_brew else None
    if system == "Linux":
        ids = {os_release.get("ID", ""), *os_release.get("ID_LIKE", "").split()}
        if ids & {"debian", "ubuntu"} and has_apt:
            return "apt"
    return None


def plan(profile: Profile, *, system: str, os_release: dict[str, str], found: dict[str, str | None]) -> dict[str, object]:
    """Describe a fixed allowlist of capabilities without running any tool."""
    manager = package_manager(system, os_release, found.get("brew") is not None, found.get("apt-get") is not None)
    registry = {tool.name: tool for tool in COMMON + PHP + DEBUG}
    try:
        selected = tuple(registry[name] for name in resolve_profile(profile))
    except KeyError as exc:
        raise ValueError(f"unapproved capability in bundled profile: {exc.args[0]}") from exc
    tools: list[dict[str, object]] = []
    packages: list[str] = []
    unmanaged: list[str] = []
    for tool in selected:
        binary = next(((cmd, found.get(cmd)) for cmd in tool.commands if found.get(cmd)), None)
        available = binary is not None
        package = tool.apt if manager == "apt" else tool.brew if manager == "brew" else None
        tools.append({
            "name": tool.name,
            "category": tool.category,
            "available": available,
            "command": binary[0] if binary else None,
            "path": binary[1] if binary else None,
            "version": None,  # Deliberately do not execute --version scripts in a read-only inventory.
            "suggested_package": package if not available else None,
        })
        if not available:
            if package:
                if package not in packages:
                    packages.append(package)
            else:
                unmanaged.append(tool.name)

    command: list[str] | None = None
    if packages and manager == "apt":
        command = ["apt-get", "install", "--", *packages]
    elif packages and manager == "brew":
        command = ["brew", "install", *packages]

    return {
        "schema": "agent-dotfiles.v1.bootstrap-plan",
        "operation": "plan",
        "profile": profile,
        "system": system,
        "distribution": os_release.get("ID") if system == "Linux" else None,
        "manager": manager,
        "tools": tools,
        "package_command_argv": command,
        "package_command_requires_approval": command is not None,
        "package_command_requires_privileges": manager == "apt" and command is not None,
        "unmanaged_missing": unmanaged,
        "warnings": [
            "This command only inspects paths. It does not download, install or execute package managers.",
            "Executable presence is not version, authenticity, sandbox or permission verification.",
            "Do not run suggested commands without reviewing OS, package sources and privileges.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only developer-tool bootstrap plan")
    parser.add_argument("operation", choices=("plan",))
    parser.add_argument("--profile", choices=("minimal", "php", "debug"), default="minimal")
    args = parser.parse_args(argv)
    system = platform.system()
    os_release: dict[str, str] = {}
    if system == "Linux":
        try:
            os_release = platform.freedesktop_os_release()
        except OSError:
            pass
    commands = {cmd for t in COMMON + PHP + DEBUG for cmd in t.commands} | {"brew", "apt-get"}
    found = {cmd: shutil.which(cmd) for cmd in sorted(commands)}
    try:
        result = plan(args.profile, system=system, os_release=os_release, found=found)
    except ValueError as exc:
        parser.exit(2, f"agent-dotfiles: invalid bundled profile: {exc}\n")
    print(json.dumps(result, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
