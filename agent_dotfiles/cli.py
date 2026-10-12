"""Agent-safe, read-only CLI. Python standard library only.

The tool deliberately does not run a shell, shell aliases, interactive dotfiles,
network installers, or commands that mutate the current repository.
"""

from __future__ import annotations

import argparse
import hashlib
import base64
import json
import os
from pathlib import Path
import selectors
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable

from . import __version__
from .validation import CommandFailure, MAX_LIMIT, _relative_path, _valid_limit

SCHEMA_VERSION = "agent-dotfiles.v1"
MAX_CAPTURE_BYTES = 2 * 1024 * 1024
PROCESS_TIMEOUT_SECONDS = 20
DEFAULT_LIMIT = 100
MAX_CONTEXT_LINES = 400
MAX_CONTEXT_FILE_BYTES = 16 * 1024 * 1024

REQUIRED_TOOLS = ("rg", "git")
OPTIONAL_TOOLS = ("jq", "curl", "fd", "shellcheck", "strace", "hyperfine", "ast-grep", "ctags", "difft", "delta")
PROFILE_ONLY_TOOLS = ("php", "composer")
PROFILE_NAMES = ("minimal", "git", "php", "shell", "debug")
PROFILE_SCHEMA = SCHEMA_VERSION + ".profile"


def _resolve_executable(name: str) -> str | None:
    """Find a real executable, not a shell alias/function."""
    path = shutil.which(name)
    return str(Path(path).resolve()) if path is not None else None


def _find_fd() -> tuple[str | None, str | None]:
    for name in ("fd", "fdfind"):
        path = _resolve_executable(name)
        if path is not None:
            return name, path
    return None, None


def _tool_inventory() -> tuple[dict[str, Any], dict[str, Any]]:
    """Report executable paths without invoking shells, installers, or aliases."""
    required: dict[str, Any] = {}
    optional: dict[str, Any] = {}
    for name in REQUIRED_TOOLS:
        executable = _resolve_executable(name)
        required[name] = {"available": executable is not None, "path": executable}
    for name in OPTIONAL_TOOLS:
        if name == "fd":
            executable_name, executable = _find_fd()
            optional[name] = {
                "available": executable is not None,
                "executable": executable_name,
                "path": executable,
            }
        else:
            executable = _resolve_executable(name)
            optional[name] = {"available": executable is not None, "path": executable}
    return required, optional


def _profile_definition(name: str) -> dict[str, Any]:
    """Load one fixed, packaged profile while rejecting executable or malformed data."""
    path = Path(__file__).resolve().parent.parent / "profiles" / f"{name}.json"
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CommandFailure("invalid_profile", f"Unable to load packaged profile {name!r}") from exc
    known_tools = set(REQUIRED_TOOLS) | set(OPTIONAL_TOOLS) | set(PROFILE_ONLY_TOOLS)
    if (not isinstance(data, dict) or set(data) != {"schema", "name", "description", "required_tools", "optional_tools", "platform_limits"}
            or data["schema"] != PROFILE_SCHEMA or data["name"] != name or not isinstance(data["description"], str)
            or not isinstance(data["required_tools"], list) or not isinstance(data["optional_tools"], list)
            or not all(isinstance(value, str) and value in known_tools for value in data["required_tools"])
            or not all(isinstance(value, str) and value in known_tools for value in data["optional_tools"])
            or set(data["required_tools"]) & set(data["optional_tools"])
            or not isinstance(data["platform_limits"], dict)):
        raise CommandFailure("invalid_profile", f"Packaged profile {name!r} is invalid")
    for tool, limit in data["platform_limits"].items():
        if (tool not in known_tools or not isinstance(limit, dict) or set(limit) != {"platforms", "reason"}
                or not isinstance(limit["platforms"], list)
                or not all(isinstance(platform, str) for platform in limit["platforms"])
                or not isinstance(limit["reason"], str)):
            raise CommandFailure("invalid_profile", f"Packaged profile {name!r} has invalid platform limits")
    return data


def _profile_report(name: str, inventory: dict[str, Any]) -> dict[str, Any]:
    """Describe one selected profile from observed binaries and declared platform bounds."""
    definition = _profile_definition(name)
    limits = definition["platform_limits"]
    tools: list[dict[str, Any]] = []
    unavailable: list[str] = []
    for role in ("required", "optional"):
        for tool in definition[f"{role}_tools"]:
            limit = limits.get(tool)
            platform_supported = limit is None or sys.platform in limit["platforms"]
            if tool in PROFILE_ONLY_TOOLS:
                # Profile capabilities must not change the default doctor JSON.
                executable = _resolve_executable(tool)
                observed = {"available": executable is not None, "path": executable}
            else:
                observed = inventory[tool]
            detail = {"name": tool, "role": role, "available": observed["available"],
                      "platform_supported": platform_supported}
            if observed.get("path") is not None:
                detail["path"] = observed["path"]
            if observed.get("executable") is not None:
                detail["executable"] = observed["executable"]
            if limit is not None:
                detail["platform_limit"] = {"platforms": limit["platforms"], "reason": limit["reason"]}
            tools.append(detail)
            if not detail["available"] or not platform_supported:
                unavailable.append(tool)
    missing_required = [entry["name"] for entry in tools
                        if entry["role"] == "required" and (not entry["available"] or not entry["platform_supported"])]
    return {"name": name, "description": definition["description"], "tools": tools,
            "unavailable": unavailable, "missing_required": missing_required,
            "ready": not missing_required}


def _doctor(strict: bool, profiles: list[str]) -> tuple[dict[str, Any], int]:
    required, optional = _tool_inventory()

    missing_required = [name for name in REQUIRED_TOOLS if not required[name]["available"]]
    report = {
        "schema": SCHEMA_VERSION + ".doctor",
        "version": __version__,
        "required": required,
        "optional": optional,
        "missing_required": missing_required,
        "shell_startup_loaded": False,
        "installation_performed": False,
    }
    if profiles:
        inventory = {**required, **optional}
        report["profiles"] = [_profile_report(name, inventory) for name in profiles]
    profile_missing = [name for profile in report.get("profiles", []) for name in profile["missing_required"]]
    return report, 2 if strict and (missing_required or profile_missing) else 0


def _files_command(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = _require_root(args.root)
    if args.engine == "rg":
        executable = _require_executable("rg")
        command = [executable, "--files", "--null", "--color=never"]
        if args.hidden:
            command.append("--hidden")
    else:
        executable_name, executable = _find_fd()
        if executable is None:
            raise CommandFailure("tool_missing", "Neither fd nor fdfind is installed")
        # Intentionally direct argv invocation; an interactive shell function
        # called fd() cannot shadow this binary.
        command = [executable, "--type", "f", "--print0", "--color", "never"]
        if args.hidden:
            command.append("--hidden")
        command.append(".")

    paths, truncated, process_exit = _collect_records(
        command,
        cwd=root,
        separator=b"\0",
        limit=args.limit,
        transform=lambda record: _filesystem_path(record),
    )
    if process_exit not in (0, None):
        raise CommandFailure("tool_failed", f"File search failed with exit code {process_exit}")
    report = {
        "schema": SCHEMA_VERSION + ".files",
        "engine": args.engine,
        "root": str(root),
        "paths": paths,
        "truncated": truncated,
        "limit": args.limit,
        "selection": {"hidden": args.hidden, "ignore_files_respected": True},
    }
    return report, 3 if truncated else 0


def _filesystem_path(raw: bytes) -> str | dict[str, str]:
    """Keep unusual filenames representable without a shell or newline splitting."""
    try:
        return raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        import base64
        return {"base64": base64.b64encode(raw).decode("ascii")}


def _parse_match(raw: bytes) -> dict[str, Any] | None:
    try:
        event: Any = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise CommandFailure("invalid_tool_output", "rg returned invalid JSON") from exc
    if not isinstance(event, dict) or event.get("type") != "match":
        return None
    data = event.get("data")
    if not isinstance(data, dict):
        raise CommandFailure("invalid_tool_output", "rg match event is missing data")
    # Preserve rg's own text/base64 fields to avoid loss of non-UTF8 paths.
    return data


def _search_command(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = _require_root(args.root)
    target = _scope_path(root, args.path)
    executable = _require_executable("rg")
    command = [
        executable,
        "--json",
        "--color=never",
        "--no-heading",
    ]
    if not args.regex:
        command.append("--fixed-strings")
    if args.hidden:
        command.append("--hidden")
    for glob in args.glob:
        command.append("--glob=" + glob)
    # -- prevents a pattern beginning with '-' from becoming a CLI option.
    command.extend(("--", args.pattern, target))
    matches, truncated, process_exit = _collect_records(
        command,
        cwd=root,
        separator=b"\n",
        limit=args.limit,
        transform=_parse_match,
    )
    if process_exit not in (0, 1, None):
        raise CommandFailure("tool_failed", f"Text search failed with exit code {process_exit}")
    report = {
        "schema": SCHEMA_VERSION + ".search",
        "mode": "regex" if args.regex else "literal",
        "root": str(root),
        "matches": matches,
        "truncated": truncated,
        "limit": args.limit,
        "selection": {"hidden": args.hidden, "ignore_files_respected": True, "path": target, "globs": args.glob},
    }
    if truncated:
        return report, 3
    return report, 0 if matches else 1


def _git_status_command(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = _require_root(args.root)
    executable = _require_executable("git")
    command = [executable, "status", "--porcelain=v1", "-z", "--untracked-files=all"]
    pending_rename: dict[str, Any] | None = None

    def parse_entry(record: bytes) -> dict[str, Any] | None:
        nonlocal pending_rename
        if pending_rename is not None:
            pending_rename["original_path"] = _filesystem_path(record)
            complete = pending_rename
            pending_rename = None
            return complete
        if len(record) < 4 or record[2:3] != b" ":
            raise CommandFailure("invalid_tool_output", "Malformed git porcelain-v1 -z status record")
        try:
            status = record[:2].decode("ascii", errors="strict")
        except UnicodeDecodeError as exc:
            raise CommandFailure("invalid_tool_output", "Invalid status bytes from git") from exc
        entry: dict[str, Any] = {"xy": status, "path": _filesystem_path(record[3:])}
        if "R" in status or "C" in status:
            # Git -z reports the destination first, then the original path.
            pending_rename = entry
            return None
        return entry

    changes, truncated, process_exit = _collect_records(
        command, cwd=root, separator=b"\0", limit=args.limit, transform=parse_entry
    )
    if pending_rename is not None and not truncated:
        raise CommandFailure("invalid_tool_output", "Git rename/copy record has no original path")
    if process_exit not in (0, None):
        raise CommandFailure("tool_failed", f"Git status failed with exit code {process_exit}")
    report = {
        "schema": SCHEMA_VERSION + ".git-status",
        "root": str(root),
        "changes": changes,
        "truncated": truncated,
        "limit": args.limit,
    }
    return report, 3 if truncated else 0



def _workspace_command(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    """Identify the exact Git checkout and return bounded, non-atomic status."""
    requested_root = _require_root(args.root)
    # An inherited Git override can make rev-parse report an ancestor checkout
    # even when --root explicitly selects a nested, independent repository.
    # Refuse ambiguity rather than silently sampling a different worktree.
    if any(name in os.environ for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")):
        raise CommandFailure(
            "invalid_repository",
            "Explicit workspace identity refuses inherited Git directory, worktree or index overrides",
        )
    git = _require_executable("git")
    try:
        top = _capture_exact([git, "rev-parse", "--show-toplevel"], cwd=requested_root)
    except CommandFailure as exc:
        if exc.reason != "tool_failed":
            raise
        raise CommandFailure("invalid_repository", f"Cannot identify Git checkout: {exc}") from exc
    checkout = Path(os.fsdecode(top.removesuffix(b"\n"))).resolve()
    if not checkout.is_dir() or (checkout != requested_root and checkout not in requested_root.parents):
        raise CommandFailure("invalid_repository", "Git resolved a checkout outside the requested root")

    def identity() -> tuple[str, str | dict[str, str] | None]:
        try:
            raw_head = _capture_exact([git, "rev-parse", "--verify", "HEAD"], cwd=checkout)
        except CommandFailure as exc:
            if exc.reason != "tool_failed":
                raise
            raise CommandFailure("missing_head", f"Git HEAD is unavailable: {exc}") from exc
        try:
            head = raw_head.removesuffix(b"\n").decode("ascii", errors="strict")
        except UnicodeDecodeError as exc:
            raise CommandFailure("invalid_tool_output", "Git HEAD contains non-ASCII bytes") from exc
        if len(head) not in (40, 64) or any(c not in "0123456789abcdef" for c in head):
            raise CommandFailure("invalid_tool_output", "Git returned an invalid HEAD object ID")
        raw_branch = _capture_exact([git, "branch", "--show-current"], cwd=checkout).removesuffix(b"\n")
        return head, _filesystem_path(raw_branch) if raw_branch else None

    before = identity()
    status, status_code = _git_status_command(argparse.Namespace(root=str(checkout), limit=args.limit))
    after = identity()
    if before != after:
        raise CommandFailure("snapshot_changed", "HEAD or branch changed while collecting Git status")

    truncated = bool(status["truncated"])
    return {
        "schema": SCHEMA_VERSION + ".workspace",
        "version": __version__,
        "tool_home": str(Path(__file__).resolve().parent.parent),
        "requested_root": str(requested_root),
        "root": str(checkout),
        "head": before[0],
        "branch": before[1],
        "detached": before[1] is None,
        "changes": status["changes"],
        "clean": None if truncated else not status["changes"],
        "truncated": truncated,
        "limit": args.limit,
        "head_unchanged_during_probe": True,
        "worktree_atomic": False,
    }, status_code


def _read_command(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    """Return an exact, digest-bound source range; never ellipsize its content."""
    root = _require_root(args.root)
    selected = _relative_path(root, args.file)
    source = root / selected
    if not source.is_file():
        raise CommandFailure("invalid_file", f"Not a regular file: {args.file}")
    size = source.stat().st_size
    if size > MAX_CONTEXT_FILE_BYTES:
        raise CommandFailure("file_too_large", f"File exceeds {MAX_CONTEXT_FILE_BYTES} bytes; use an exact source-specific reader")
    if args.end < args.start or args.end - args.start + 1 > MAX_CONTEXT_LINES:
        raise CommandFailure("invalid_range", f"Range must be increasing and at most {MAX_CONTEXT_LINES} lines")
    raw = source.read_bytes()
    if b"\0" in raw:
        raise CommandFailure("binary_file", "Refusing to present binary data as source lines")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise CommandFailure("invalid_encoding", "Source is not UTF-8; no lossy decoding performed") from exc
    # Unlike str.splitlines(), this follows Git/rg LF line numbering. CRLF and
    # Unicode line-separator characters remain unchanged in the selected bytes.
    parts = text.split("\n")
    lines = [part + "\n" for part in parts[:-1]]
    if parts[-1]:
        lines.append(parts[-1])
    if args.start > max(1, len(lines)):
        raise CommandFailure("invalid_range", f"Start line {args.start} exceeds file length {len(lines)}")
    actual_end = min(args.end, len(lines))
    content = "".join(lines[args.start - 1:actual_end])
    content_bytes = content.encode("utf-8")
    if len(content_bytes) > MAX_CAPTURE_BYTES:
        raise CommandFailure("range_too_large", "Requested exact range exceeds the output byte limit; request fewer lines")
    return {
        "schema": SCHEMA_VERSION + ".read",
        "root": str(root),
        "path": selected,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "total_lines": len(lines),
        "start": args.start,
        "requested_end": args.end,
        "actual_end": actual_end,
        "complete_file": args.start == 1 and actual_end == len(lines),
        "content": content,
        "content_bytes": len(content_bytes),
        "truncated": False,
    }, 0


def _scope_path(root: Path, path: str) -> str:
    if path == ".":
        return "."
    relative = _relative_path(root, path)
    if not (root / relative).exists():
        raise CommandFailure("invalid_scope", f"Path does not exist: {path}")
    return relative


def _tracked_command(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = _require_root(args.root)
    executable = _require_executable("git")
    command = [executable, "ls-files", "--cached", "--full-name", "-z"]
    paths, truncated, process_exit = _collect_records(
        command, cwd=root, separator=b"\0", limit=args.limit, transform=_filesystem_path
    )
    if process_exit not in (0, None):
        raise CommandFailure("tool_failed", f"Git tracked-files failed with exit code {process_exit}")
    return {
        "schema": SCHEMA_VERSION + ".tracked",
        "root": str(root),
        "paths": paths,
        "limit": args.limit,
        "truncated": truncated,
        "selection": "git-index-only; ignores untracked and excluded files",
    }, 3 if truncated else 0


def _capture_exact(command: list[str], *, cwd: Path) -> bytes:
    """Capture only complete output or fail; no partial patch is ever returned."""
    with tempfile.TemporaryFile(mode="w+b") as stderr_file:
        try:
            process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=stderr_file, shell=False,
                                       env={**os.environ, "GIT_PAGER": "cat", "GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C", "GIT_LITERAL_PATHSPECS": "1"})
        except OSError as exc:
            raise CommandFailure("spawn_failed", f"Could not execute {Path(command[0]).name}: {exc}") from exc
        captured = bytearray()
        try:
            if process.stdout is None:
                raise CommandFailure("spawn_failed", "No stdout pipe from process")
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                deadline = time.monotonic() + PROCESS_TIMEOUT_SECONDS
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0 or not selector.select(timeout=remaining):
                        raise CommandFailure("timeout", f"Command exceeded {PROCESS_TIMEOUT_SECONDS}s")
                    chunk = os.read(process.stdout.fileno(), 16 * 1024)
                    if not chunk:
                        break
                    captured.extend(chunk)
                    if len(captured) > MAX_CAPTURE_BYTES:
                        raise CommandFailure("output_too_large", "Patch exceeds exact-output cap: narrow --file or use git directly; no partial patch returned")
            process_exit = process.wait(timeout=3)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=3)
            if process.stdout is not None:
                process.stdout.close()
        if process_exit != 0:
            stderr_file.seek(0)
            message = stderr_file.read(4096).decode("utf-8", "replace").strip()
            raise CommandFailure("tool_failed", f"Git exited {process_exit}: {message}")
        return bytes(captured)


def _indexed_path(executable: str, root: Path, selected: str) -> bool:
    """Distinguish a clean indexed file from content omitted by Git diff.

    This is called only for empty patches: an untracked or ignored source file
    is not covered by git diff and must not look like verified empty evidence.
    """
    # ls-files without --error-unmatch returns empty output for absent paths.
    # Reuse bounded capture: even a literal directory can select descendants.
    indexed = _capture_exact([executable, "ls-files", "-z", "--", selected], cwd=root)
    return indexed == os.fsencode(selected) + b"\0"



def _git_patch_command(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = _require_root(args.root)
    selected = _relative_path(root, args.file)
    if (root / selected).is_dir():
        raise CommandFailure("invalid_file", "git-patch requires an exact file, not a directory")
    executable = _require_executable("git")
    command = [executable, "diff", "--no-ext-diff", "--no-textconv", "--no-color", "--binary", "--full-index"]
    if args.staged:
        command.append("--cached")
    if args.base is not None:
        if args.base.startswith("-") or not args.base.strip():
            raise CommandFailure("invalid_ref", "Base revision cannot begin with '-' or be empty")
        command.append(args.base)
    # Even literal pathspecs can select directory descendants. Recheck which
    # changed filenames Git selected before claiming single-file evidence.
    raw = _capture_exact([*command, "--", selected], cwd=root)
    if raw:
        changed = _capture_exact([*command, "--name-only", "--relative", "-z", "--", selected], cwd=root)
        if changed != os.fsencode(selected) + b"\0":
            raise CommandFailure(
                "ambiguous_path",
                "Git diff selected a different path or multiple paths; choose one exact file.",
            )
    if not raw and not _indexed_path(executable, root, selected):
        raise CommandFailure(
            "path_not_in_diff",
            "No Git patch: path is absent from the index; Git diff omits untracked and ignored "
            "files. Use git-status and read to inspect current contents.",
        )
    try:
        payload: dict[str, str] = {"text": raw.decode("utf-8", errors="strict")}
    except UnicodeDecodeError:
        payload = {"base64": base64.b64encode(raw).decode("ascii")}
    return {
        "schema": SCHEMA_VERSION + ".git-patch",
        "root": str(root),
        "path": selected,
        "staged": args.staged,
        "base": args.base,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "patch": payload,
        "truncated": False,
    }, 0


def _require_executable(name: str) -> str:
    executable = _resolve_executable(name)
    if executable is None:
        raise CommandFailure("tool_missing", f"Required executable {name!r} is unavailable in PATH")
    return executable


def _require_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        raise CommandFailure("invalid_root", f"Not a directory: {raw}")
    return root


def _collect_records(
    command: list[str],
    *,
    cwd: Path,
    separator: bytes,
    limit: int,
    transform: Callable[[bytes], Any | None],
) -> tuple[list[Any], bool, int | None]:
    """Read bounded output from subprocess argv without shell interpretation.

    Output beyond the configured record/byte limits is *explicitly* reported
    as truncated (exit code 3), never treated as complete evidence.
    """
    records: list[Any] = []
    pending = bytearray()
    total_bytes = 0
    truncated = False
    process_exit: int | None = None

    with tempfile.TemporaryFile(mode="w+b") as stderr_file:
        try:
            process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=stderr_file, shell=False,
                                       env={**os.environ, "RIPGREP_CONFIG_PATH": os.devnull, "GIT_PAGER": "cat", "GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C", "NO_COLOR": "1"})
        except OSError as exc:
            raise CommandFailure("spawn_failed", f"Could not execute {Path(command[0]).name}: {exc}") from exc

        try:
            if process.stdout is None:
                raise CommandFailure("spawn_failed", "No stdout pipe from process")
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                deadline = time.monotonic() + PROCESS_TIMEOUT_SECONDS
                eof = False
                while not eof:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise CommandFailure("timeout", f"Command exceeded {PROCESS_TIMEOUT_SECONDS}s")
                    if not selector.select(timeout=remaining):
                        raise CommandFailure("timeout", f"Command exceeded {PROCESS_TIMEOUT_SECONDS}s")
                    chunk = os.read(process.stdout.fileno(), 16 * 1024)
                    if not chunk:
                        eof = True
                    else:
                        total_bytes += len(chunk)
                        if total_bytes > MAX_CAPTURE_BYTES:
                            truncated = True
                            break
                        pending.extend(chunk)
                    while separator in pending:
                        end = pending.index(separator)
                        record = bytes(pending[:end])
                        del pending[:end + len(separator)]
                        if not record:
                            continue
                        parsed = transform(record)
                        if parsed is not None:
                            if len(records) >= limit:
                                truncated = True
                                break
                            records.append(parsed)
                    if truncated:
                        break
            if truncated:
                process.kill()
                process.wait(timeout=3)
            else:
                process_exit = process.wait(timeout=3)
                if pending:
                    raise CommandFailure("invalid_tool_output", "Command output ended with an incomplete record")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=3)
            if process.stdout is not None:
                process.stdout.close()

        stderr_file.seek(0)
        stderr_message = stderr_file.read(4096).decode("utf-8", errors="replace").strip()
        if not truncated and process_exit not in (0, 1) and stderr_message:
            raise CommandFailure("tool_failed", stderr_message)

    return records, truncated, process_exit


def _positive_int(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Expected positive integer") from exc
    if value < 1:
        raise argparse.ArgumentTypeError("Expected positive integer")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Non-interactive, bounded CLI for coding agents")
    parser.add_argument("--version", action="version", version=__version__)
    subcommands = parser.add_subparsers(dest="command", required=True)

    doctor = subcommands.add_parser("doctor", help="Read-only executable inventory")
    doctor.add_argument("--strict", action="store_true", help="Exit 2 if rg or git is missing")
    doctor.add_argument("--profile", action="append", choices=PROFILE_NAMES, default=[],
                        help="Report one fixed capability profile; repeatable and non-mutating")

    files = subcommands.add_parser("files", help="Bounded NUL-safe file discovery")
    files.add_argument("--root", default=".")
    files.add_argument("--engine", choices=("rg", "fd"), default="rg")
    files.add_argument("--hidden", action="store_true")
    files.add_argument("--limit", type=_valid_limit, default=DEFAULT_LIMIT)

    search = subcommands.add_parser("search", help="Bounded literal/regex match evidence")
    search.add_argument("pattern", help="Pattern (literal unless --regex is used)")
    search.add_argument("--root", default=".")
    search.add_argument("--regex", action="store_true")
    search.add_argument("--hidden", action="store_true")
    search.add_argument("--path", default=".", help="Search only within this file or directory")
    search.add_argument("--glob", action="append", default=[], help="rg include/exclude glob; repeatable")
    search.add_argument("--limit", type=_valid_limit, default=DEFAULT_LIMIT)

    git_status = subcommands.add_parser("git-status", help="NUL-safe porcelain worktree changes")
    git_status.add_argument("--root", default=".")
    git_status.add_argument("--limit", type=_valid_limit, default=DEFAULT_LIMIT)

    workspace = subcommands.add_parser("workspace", help="Bounded Git checkout identity and worktree status")
    workspace.add_argument("--root", default=".")
    workspace.add_argument("--limit", type=_valid_limit, default=DEFAULT_LIMIT)

    read = subcommands.add_parser("read", help="Full-fidelity UTF-8 source range with file SHA-256")
    read.add_argument("file", help="A single file within --root")
    read.add_argument("--root", default=".")
    read.add_argument("--start", type=_positive_int, default=1)
    read.add_argument("--end", type=_positive_int, default=80)

    tracked = subcommands.add_parser("tracked", help="NUL-safe Git index file paths")
    tracked.add_argument("--root", default=".")
    tracked.add_argument("--limit", type=_valid_limit, default=DEFAULT_LIMIT)

    patch = subcommands.add_parser("git-patch", help="Complete, digest-bound Git patch for one exact path")
    patch.add_argument("file")
    patch.add_argument("--root", default=".")
    patch.add_argument("--staged", action="store_true")
    patch.add_argument("--base", help="Optional Git revision to compare against; defaults to worktree diff")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "doctor":
            report, exit_code = _doctor(args.strict, args.profile)
        elif args.command == "files":
            report, exit_code = _files_command(args)
        elif args.command == "search":
            report, exit_code = _search_command(args)
        elif args.command == "git-status":
            report, exit_code = _git_status_command(args)
        elif args.command == "workspace":
            report, exit_code = _workspace_command(args)
        elif args.command == "read":
            report, exit_code = _read_command(args)
        elif args.command == "tracked":
            report, exit_code = _tracked_command(args)
        elif args.command == "git-patch":
            report, exit_code = _git_patch_command(args)
        else:
            raise AssertionError("Unreachable command")
    except CommandFailure as exc:
        print(json.dumps({"schema": SCHEMA_VERSION + ".error", "error": exc.reason, "message": str(exc)}, ensure_ascii=True))
        return 2
    print(json.dumps(report, ensure_ascii=True, separators=(",", ":")))
    return exit_code
