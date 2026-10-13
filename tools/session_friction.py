#!/usr/bin/env python3
"""Mine coding-agent session traces for candidate friction.

This is maintainer-side experiment tooling. It reads local JSON/JSONL input,
prints a deterministic JSON report, and never mutates the source trace.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b([A-Z0-9_]*(?:TOKEN|PASSWORD|SECRET|API_KEY|APIKEY)[A-Z0-9_]*)=([^\s]+)"
)
SECRET_OPTION = re.compile(
    r"(?i)(--(?:token|password|secret|api[-_]?key)(?:=|\s+))([^\s]+)"
)
WHITESPACE = re.compile(r"\s+")


class TraceError(ValueError):
    """Raised when a trace cannot be parsed safely."""


@dataclass(frozen=True)
class Event:
    index: int
    kind: str
    signature: str
    success: bool | None = None
    tool: str | None = None
    error_hint: str | None = None


@dataclass(frozen=True)
class Candidate:
    kind: str
    occurrences: int
    event_indexes: tuple[int, ...]
    sample: str
    reason: str


def _redact(value: str, limit: int = 180) -> str:
    value = SECRET_ASSIGNMENT.sub(r"\1=<redacted>", value)
    value = SECRET_OPTION.sub(r"\1<redacted>", value)
    value = value.replace("\n", " ")
    value = WHITESPACE.sub(" ", value).strip()
    if len(value) > limit:
        return value[: limit - 1] + "…"
    return value


def _normalize(value: str) -> str:
    return WHITESPACE.sub(" ", value.strip())


def _walk(value: Any) -> Iterator[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key), child
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _first_value(record: dict[str, Any], keys: set[str]) -> Any | None:
    lowered = {key.lower() for key in keys}
    for key, value in _walk(record):
        if key.lower() in lowered:
            return value
    return None


def _first_string(record: dict[str, Any], keys: set[str]) -> str | None:
    value = _first_value(record, keys)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _tool_name(record: dict[str, Any]) -> str | None:
    direct = _first_string(record, {"tool_name", "tool"})
    if direct:
        return direct

    function = record.get("function")
    if isinstance(function, dict):
        name = function.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()

    name = record.get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()

    return None


def _success(record: dict[str, Any]) -> bool | None:
    exit_code = _first_value(record, {"exit_code", "return_code", "returncode"})
    if isinstance(exit_code, int):
        return exit_code == 0
    if isinstance(exit_code, str) and exit_code.lstrip("-").isdigit():
        return int(exit_code) == 0

    status = _first_value(record, {"status", "conclusion"})
    if isinstance(status, bool):
        return status
    if isinstance(status, str):
        normalized = status.strip().lower()
        if normalized in {"success", "succeeded", "completed", "ok", "passed"}:
            return True
        if normalized in {"failure", "failed", "error", "cancelled", "timed_out"}:
            return False

    return None


def _error_hint(record: dict[str, Any]) -> str | None:
    value = _first_string(record, {"stderr", "error"})
    if value:
        return _redact(value, 120)
    return None


def _command(record: dict[str, Any]) -> str | None:
    value = _first_value(record, {"command", "cmd", "shell_command"})
    if isinstance(value, str) and value.strip():
        return _normalize(value)

    argv = _first_value(record, {"argv"})
    if isinstance(argv, list) and argv and all(isinstance(item, str) for item in argv):
        return " ".join(shlex.quote(item) for item in argv)

    return None


def _normalized_event(record: dict[str, Any], index: int) -> Event | None:
    kind = record.get("kind")
    value = record.get("value")
    if not isinstance(kind, str) or not isinstance(value, str) or not value.strip():
        return None

    kind = kind.strip().lower()
    if kind not in {"command", "read", "search", "write"}:
        return None

    success = record.get("success")
    if not isinstance(success, bool):
        success = None

    tool = record.get("tool")
    if not isinstance(tool, str):
        tool = None

    return Event(
        index=index,
        kind=kind,
        signature=_normalize(value),
        success=success,
        tool=tool,
        error_hint=None,
    )


def _auto_event(record: dict[str, Any], index: int) -> Event | None:
    command = _command(record)
    tool = _tool_name(record)
    tool_lower = (tool or "").lower()

    if command:
        return Event(
            index=index,
            kind="command",
            signature=command,
            success=_success(record),
            tool=tool,
            error_hint=_error_hint(record),
        )

    path = _first_string(record, {"file_path", "filepath", "path", "filename"})
    if path and any(token in tool_lower for token in ("read", "open", "view", "cat")):
        return Event(index, "read", _normalize(path), _success(record), tool)

    query = _first_string(record, {"query", "pattern", "search"})
    if query and any(token in tool_lower for token in ("search", "grep", "find", "ripgrep")):
        return Event(index, "search", _normalize(query), _success(record), tool)

    return None


def _records_from_json(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]

    if isinstance(value, dict):
        for key in ("events", "messages", "items", "records"):
            nested = value.get(key)
            if isinstance(nested, list):
                return [item for item in nested if isinstance(item, dict)]
        return [value]

    raise TraceError("top-level JSON must be an object or array")


def load_records(path: Path) -> list[dict[str, Any]]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TraceError(f"{path}: {exc}") from exc

    stripped = raw.lstrip()
    if not stripped:
        return []

    if stripped.startswith("["):
        try:
            return _records_from_json(json.loads(raw))
        except json.JSONDecodeError as exc:
            raise TraceError(f"{path}:{exc.lineno}:{exc.colno}: invalid JSON") from exc

    if stripped.startswith("{"):
        try:
            whole = json.loads(raw)
        except json.JSONDecodeError:
            whole = None
        if whole is not None:
            return _records_from_json(whole)

    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TraceError(f"{path}:{line_number}:{exc.colno}: invalid JSONL") from exc
        if isinstance(value, dict):
            records.append(value)

    return records


def normalize_records(
    records: Sequence[dict[str, Any]], input_format: str
) -> list[Event]:
    events: list[Event] = []
    for index, record in enumerate(records, 1):
        event = (
            _normalized_event(record, index)
            if input_format == "normalized"
            else _normalized_event(record, index) or _auto_event(record, index)
        )
        if event is not None:
            events.append(event)

    return events


def _executable(command: str) -> str:
    try:
        parts = shlex.split(command)
    except ValueError:
        parts = command.split()

    while parts and "=" in parts[0] and not parts[0].startswith(("./", "/")):
        key, _, _ = parts[0].partition("=")
        if key.replace("_", "").isalnum():
            parts.pop(0)
        else:
            break

    return parts[0] if parts else command


def find_candidates(events: Sequence[Event]) -> list[Candidate]:
    candidates: list[Candidate] = []
    grouped: dict[tuple[str, str], list[Event]] = defaultdict(list)

    for event in events:
        grouped[(event.kind, event.signature)].append(event)

    for (kind, signature), group in sorted(grouped.items()):
        threshold = 3 if kind in {"command", "read", "search"} else 4
        if len(group) >= threshold:
            candidates.append(
                Candidate(
                    kind=f"repeated_{kind}",
                    occurrences=len(group),
                    event_indexes=tuple(event.index for event in group),
                    sample=_redact(signature),
                    reason=f"same {kind} observed at least {threshold} times",
                )
            )

        failures = [event for event in group if event.success is False]
        if kind == "command" and len(failures) >= 2:
            candidates.append(
                Candidate(
                    kind="repeated_failed_command",
                    occurrences=len(failures),
                    event_indexes=tuple(event.index for event in failures),
                    sample=_redact(signature),
                    reason="same command failed at least twice",
                )
            )

    failed_by_executable: dict[str, list[Event]] = defaultdict(list)
    for event in events:
        if event.kind == "command" and event.success is False:
            failed_by_executable[_executable(event.signature)].append(event)

    for executable, failures in sorted(failed_by_executable.items()):
        signatures = {event.signature for event in failures}
        if len(failures) >= 3 and len(signatures) >= 2:
            candidates.append(
                Candidate(
                    kind="command_failure_churn",
                    occurrences=len(failures),
                    event_indexes=tuple(event.index for event in failures),
                    sample=_redact(executable),
                    reason="multiple variants of the same executable failed",
                )
            )

    return sorted(candidates, key=lambda item: (item.kind, item.sample, item.event_indexes))


def analyze(paths: Iterable[Path], input_format: str) -> dict[str, Any]:
    events: list[Event] = []
    source_counts: dict[str, int] = {}

    for path in paths:
        records = load_records(path)
        source_counts[str(path)] = len(records)
        offset = len(events)
        normalized = normalize_records(records, input_format)
        events.extend(
            Event(
                index=event.index + offset,
                kind=event.kind,
                signature=event.signature,
                success=event.success,
                tool=event.tool,
                error_hint=event.error_hint,
            )
            for event in normalized
        )

    kinds = Counter(event.kind for event in events)
    failures = sum(event.success is False for event in events)
    candidates = find_candidates(events)

    return {
        "schema": "agent-dotfiles.session-friction.v0",
        "sources": source_counts,
        "events": {
            "recognized": len(events),
            "by_kind": dict(sorted(kinds.items())),
            "failed": failures,
        },
        "candidates": [asdict(candidate) for candidate in candidates],
        "interpretation": "Candidates are observations for human review, not dotfile recommendations.",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read local JSON/JSONL coding-agent traces and flag candidate friction."
    )
    parser.add_argument("trace", nargs="+", type=Path)
    parser.add_argument(
        "--input-format",
        choices=("auto", "normalized"),
        default="auto",
        help="auto extracts common nested tool-call shapes; normalized uses kind/value events",
    )
    parser.add_argument("--pretty", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = analyze(args.trace, args.input_format)
    except TraceError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    json.dump(report, sys.stdout, indent=2 if args.pretty else None, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
