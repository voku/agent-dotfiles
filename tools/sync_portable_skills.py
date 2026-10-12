#!/usr/bin/env python3
"""Sync the reviewed portable skill selection from a local, pinned checkout."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Final


SCHEMA: Final = "agent-dotfiles.v1.portable-skills"
SKILLS: Final = (
    "coding-simplicity",
    "testing-best-practices",
    "php-static-analysis",
    "language-onboarding-authoring",
)
MANIFEST: Final = "skills/portable-skills.json"
CANONICAL_SOURCE_URLS: Final = {
    "https://github.com/voku/agent-skills",
    "ssh://git@github.com/voku/agent-skills",
    "git@github.com:voku/agent-skills",
}


class SyncError(Exception):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def regular_directory(value: Path, label: str) -> Path:
    raw = Path(os.path.abspath(value.expanduser()))
    if ".." in raw.parts or not raw.is_dir():
        raise SyncError(f"{label} must be an existing directory without traversal")
    for ancestor in (raw, *raw.parents):
        if not ancestor.is_symlink():
            continue
        # macOS commonly exposes the same temporary directory through /var and
        # /private/var. This is the sole system alias accepted before operating
        # on the canonical path; supplied symlinked roots and ancestors remain
        # refused.
        if (sys.platform == "darwin" and ancestor == Path("/var")
                and ancestor.resolve(strict=True) == Path("/private/var")):
            continue
        raise SyncError(f"{label} must not use a symlinked path")
    candidate = raw.resolve(strict=True)
    return candidate


def git(source: Path, *arguments: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(source), *arguments],
        capture_output=True,
        check=False,
        timeout=30,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
    )
    if result.returncode:
        raise SyncError("portable skill source verification failed")
    return result.stdout


def source_files(source: Path, revision: str) -> dict[str, bytes]:
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise SyncError("revision must be a full 40-character Git commit SHA")
    if not source.is_dir() or git(source, "rev-parse", "--show-toplevel").removesuffix(b"\n") != os.fsencode(source):
        raise SyncError("source must be the Git checkout root")
    if git(source, "rev-parse", "HEAD").decode().strip() != revision:
        raise SyncError("source HEAD does not match the pinned revision")
    if git(source, "status", "--porcelain=v1", "-z", "--untracked-files=no"):
        raise SyncError("tracked source files must be clean")
    origin = git(source, "remote", "get-url", "origin").decode("utf-8").strip().removesuffix(".git")
    if origin not in CANONICAL_SOURCE_URLS:
        raise SyncError("source origin must identify voku/agent-skills")

    files: dict[str, bytes] = {}
    for skill in SKILLS:
        prefix = f"skills/{skill}/"
        listing = git(source, "ls-tree", "-r", "-z", revision, "--", f"skills/{skill}")
        for record in (entry for entry in listing.split(b"\0") if entry):
            metadata, raw_path = record.split(b"\t", 1)
            mode, kind, _object = metadata.decode("ascii").split(" ", 2)
            path = os.fsdecode(raw_path)
            relative = PurePosixPath(path)
            if (mode not in {"100644", "100755"} or kind != "blob" or not path.startswith(prefix)
                    or ".." in relative.parts or relative.parts[0] != "skills"):
                raise SyncError("portable skill source must contain only regular files")
            data = git(source, "show", f"{revision}:{path}")
            working = source / path
            if not working.is_file() or working.is_symlink() or working.read_bytes() != data:
                raise SyncError("portable skill source differs from pinned commit")
            files[path] = data
        if f"skills/{skill}/SKILL.md" not in files:
            raise SyncError(f"required portable skill is missing: {skill}")
    return dict(sorted(files.items()))


def destination_path(destination: Path, relative: str) -> Path:
    """Return a target below destination only when no existing component is a symlink."""
    target = destination
    for part in PurePosixPath(relative).parts:
        target /= part
        if target.is_symlink():
            raise SyncError("destination must not contain symlinked path components")
    return target


def verify_previous_snapshot(destination: Path) -> set[str]:
    """Return the verified current snapshot paths before an explicit replacement."""
    manifest_path = destination_path(destination, MANIFEST)
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise SyncError("portable skill replacement requires the current provenance manifest")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SyncError("portable skill replacement requires a valid provenance manifest") from error
    if not isinstance(manifest, dict):
        raise SyncError("portable skill replacement requires a valid provenance manifest")
    source = manifest.get("source")
    skills = manifest.get("skills")
    if (manifest.get("schema") != SCHEMA or not isinstance(source, dict)
            or not isinstance(skills, dict)
            or source.get("repository") != "voku/agent-skills"
            or not re.fullmatch(r"[0-9a-f]{40}", source.get("revision", ""))
            or set(skills) != set(SKILLS)):
        raise SyncError("portable skill replacement requires a complete provenance manifest")

    known: set[str] = set()
    for skill in SKILLS:
        entries = skills[skill].get("files") if isinstance(skills[skill], dict) else None
        if not isinstance(entries, dict) or f"SKILL.md" not in entries:
            raise SyncError("portable skill replacement requires complete provenance files")
        for relative, expected_digest in entries.items():
            pure = PurePosixPath(relative)
            if (not isinstance(relative, str) or pure.is_absolute() or not pure.parts
                    or ".." in pure.parts or not re.fullmatch(r"[0-9a-f]{64}", expected_digest)):
                raise SyncError("portable skill replacement has unsafe provenance files")
            path = f"skills/{skill}/{relative}"
            target = destination_path(destination, path)
            if target.is_symlink() or not target.is_file() or digest(target.read_bytes()) != expected_digest:
                raise SyncError("portable skill replacement refuses a changed snapshot")
            known.add(path)

        root = destination_path(destination, f"skills/{skill}")
        actual: set[str] = set()
        for base, dirs, names in os.walk(root, followlinks=False):
            for name in dirs + names:
                child = Path(base) / name
                if child.is_symlink():
                    raise SyncError("portable skill replacement refuses symlinked snapshot files")
            actual.update((Path(base) / name).relative_to(destination).as_posix() for name in names)
        if actual != {path for path in known if path.startswith(f"skills/{skill}/")}:
            raise SyncError("portable skill replacement refuses an incomplete or expanded snapshot")
    return known


def sync(source: Path, revision: str, destination: Path, *, preview: bool = False,
         replace: bool = False) -> dict[str, object]:
    source = regular_directory(source, "source")
    destination = regular_directory(destination, "destination")
    if source == destination:
        raise SyncError("source and destination must be separate checkouts")
    files = source_files(source, revision)
    manifest = {
        "schema": SCHEMA,
        "source": {"repository": "voku/agent-skills", "revision": revision},
        "skills": {skill: {"files": {
            path.removeprefix(f"skills/{skill}/"): digest(data)
            for path, data in files.items() if path.startswith(f"skills/{skill}/")
        }} for skill in SKILLS},
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    expected = {**files, MANIFEST: manifest_bytes}
    replacement_needed = any(
        (target := destination_path(destination, path)).exists()
        and (target.is_symlink() or not target.is_file() or target.read_bytes() != data)
        for path, data in expected.items()
    )
    if replacement_needed:
        if not replace:
            raise SyncError("refusing to replace existing portable skill file without --replace")
        previous = verify_previous_snapshot(destination)
        if previous != set(files):
            raise SyncError("portable skill replacement requires the same selected file set")
    for path, data in expected.items():
        target = destination_path(destination, path)
        if target.exists() or target.is_symlink():
            if (not target.is_file() or target.is_symlink()
                    or (target.read_bytes() != data and not replace)):
                raise SyncError(f"refusing to replace existing portable skill file: {path}")
    if not preview:
        for path, data in expected.items():
            target = destination_path(destination, path)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or target.read_bytes() != data:
                target.write_bytes(data)
    return {"source_revision": revision, "skills": list(SKILLS), "files": len(files),
            "replaced": replacement_needed}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--source", required=True, help="clean local voku/agent-skills checkout")
    parser.add_argument("--revision", required=True, help="full source commit SHA")
    parser.add_argument("--destination", required=True, help="agent-dotfiles checkout root")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--replace", action="store_true",
                        help="replace only an unchanged, verified existing portable snapshot")
    args = parser.parse_args()
    try:
        result = sync(Path(args.source), args.revision, Path(args.destination), preview=args.dry_run,
                      replace=args.replace)
        print(json.dumps({"schema": SCHEMA, "operation": "sync", "ok": True, **result}))
        return 0
    except (SyncError, OSError, UnicodeError, subprocess.SubprocessError) as error:
        print(json.dumps({"schema": SCHEMA, "operation": "sync", "ok": False, "error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
