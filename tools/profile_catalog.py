"""Strict, non-executable Redpill capability profiles for first-install planning.

Only fixed files bundled with the reviewed checkout are loaded. No project override,
shell evaluation, network access, or profile-driven command execution is supported.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA = "agent-dotfiles.v1.capability-profile"
SUPPORTED = ("minimal", "php", "debug")
PROFILE_DIRECTORY = Path(__file__).resolve().parents[1] / ".redpill" / "profiles"


def resolve_profile(name: str, *, directory: Path | None = None) -> tuple[str, ...]:
    """Resolve the fixed inheritance graph while rejecting corrupt bundled data.

    The optional directory parameter is only for isolated validation fixtures; the
    executable always reads the profile directory adjacent to its own source.
    """
    if name not in SUPPORTED:
        raise ValueError(f"unsupported profile: {name}")

    root = PROFILE_DIRECTORY if directory is None else directory
    completed: set[str] = set()
    active: set[str] = set()
    tools: list[str] = []
    known_tools: set[str] = set()

    def visit(current: str) -> None:
        if current in active:
            raise ValueError(f"profile inheritance cycle: {current}")
        if current in completed:
            return
        if current not in SUPPORTED:
            raise ValueError(f"unsupported parent profile: {current}")

        path = root / f"{current}.json"
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing, non-regular or symlinked profile: {current}")
        try:
            value: Any = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"unreadable profile {current}: {exc}") from exc

        if not isinstance(value, dict) or set(value) != {"schema", "name", "extends", "tools"}:
            raise ValueError(f"invalid profile fields: {current}")
        if value["schema"] != SCHEMA or value["name"] != current:
            raise ValueError(f"invalid schema or identity: {current}")
        parents: Any = value["extends"]
        items: Any = value["tools"]
        if not isinstance(parents, list) or not all(isinstance(p, str) for p in parents):
            raise ValueError(f"invalid parent list: {current}")
        if not isinstance(items, list) or not items or not all(isinstance(t, str) for t in items):
            raise ValueError(f"invalid capability list: {current}")
        if len(set(parents)) != len(parents) or len(set(items)) != len(items):
            raise ValueError(f"duplicate entries: {current}")
        if parents != ([] if current == "minimal" else ["minimal"]):
            raise ValueError(f"invalid fixed inheritance: {current}")

        active.add(current)
        for parent in parents:
            visit(parent)
        for tool in items:
            if tool in known_tools:
                raise ValueError(f"duplicate inherited capability: {tool}")
            known_tools.add(tool)
            tools.append(tool)
        active.remove(current)
        completed.add(current)

    visit(name)
    return tuple(tools)
