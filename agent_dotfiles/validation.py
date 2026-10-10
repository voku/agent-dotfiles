"""Pure safety/boundary validation for agent CLI inputs.

Isolated so mutation testing can cheaply exercise critical denial paths.
"""

from __future__ import annotations

import argparse
from pathlib import Path

MAX_LIMIT = 1000


class CommandFailure(Exception):
    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


def _relative_path(root: Path, path: str) -> str:
    if not path or path == ".":
        raise CommandFailure("invalid_file", "A specific file path is required")
    candidate = Path(path)
    resolved = (root / candidate).resolve()
    try:
        relative = resolved.relative_to(root)
    except ValueError as exc:
        raise CommandFailure("path_escape", f"File resolves outside selected root: {path}") from exc
    if str(relative) == ".":
        raise CommandFailure("invalid_file", "Root directory is not a file")
    return relative.as_posix()


def _valid_limit(raw: str) -> int:
    try:
        limit = int(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("limit must be an integer") from exc
    if not 1 <= limit <= MAX_LIMIT:
        raise argparse.ArgumentTypeError(f"limit must be between 1 and {MAX_LIMIT}")
    return limit


