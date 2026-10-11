#!/usr/bin/env python3
"""Offline, pinned installation into an explicit private prefix (Python 3.10+)."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import tempfile

SCHEMA = "agent-dotfiles.v1.installation"
MANIFEST = "installation.json"
SHELL_FILES = {".bashrc", ".zshrc", ".shellrc", ".functions", ".exports"}
SHELL_MODULES = {"shell/modules/context.sh", "shell/modules/git.sh"}
LAUNCHER = b'''#!/usr/bin/env python3
"""Explicitly activated isolated agent-dotfiles; do not create bytecode."""
import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent_dotfiles.cli import main
raise SystemExit(main())
'''


class SetupError(Exception):
    pass


def safe_path(value: str) -> Path:
    # Reject lexical traversal and every symlink ancestor before resolution.
    candidate = Path(value).expanduser()
    if ".." in candidate.parts:
        raise SetupError("path traversal is not permitted")
    candidate = Path(os.path.abspath(candidate))
    if candidate == Path(candidate.anchor):
        raise SetupError("filesystem root is not an installation prefix")
    for component in (candidate, *candidate.parents):
        if component.is_symlink():
            raise SetupError("symlink paths are not permitted")
    return candidate


def git(source: Path, *arguments: str) -> bytes:
    result = subprocess.run(["git", "-C", str(source), *arguments],
                            capture_output=True, check=False, timeout=30)
    if result.returncode:
        raise SetupError("Git source verification failed")
    return result.stdout


def runtime_path(name: str) -> bool:
    path = PurePosixPath(name)
    return (len(path.parts) >= 2 and path.parts[0] == "agent_dotfiles"
            and path.suffix == ".py" and ".." not in path.parts
            and all(re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", part)
                    for part in (*path.parts[1:-1], path.stem)))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def install(source: Path, revision: str, prefix: Path, *, preview: bool = False) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise SetupError("revision must be a full 40-character Git commit SHA")
    if not source.is_dir() or git(source, "rev-parse", "--show-toplevel").removesuffix(b"\n") != os.fsencode(source):
        raise SetupError("source must be the Git checkout root")
    if git(source, "rev-parse", "HEAD").decode().strip() != revision:
        raise SetupError("source HEAD does not match the pinned revision")
    if git(source, "status", "--porcelain=v1", "-z", "--untracked-files=no"):
        raise SetupError("tracked source files must be clean")
    if prefix == source or source in prefix.parents or prefix in source.parents:
        raise SetupError("prefix and source must be separate directories")
    if not prefix.parent.is_dir():
        raise SetupError("prefix parent must already exist")
    if prefix.exists() and (not prefix.is_dir() or any(prefix.iterdir())):
        raise SetupError("existing prefix must be an empty directory")
    tracked = git(source, "ls-files", "-z").split(b"\0")
    paths = [os.fsdecode(name) for name in tracked if name]
    paths = [name for name in paths if name in {"LICENSE", "bin/agent-dotfiles"} | SHELL_FILES | SHELL_MODULES or runtime_path(name)]
    required = {"LICENSE", "bin/agent-dotfiles", "agent_dotfiles/__init__.py", "agent_dotfiles/cli.py"} | SHELL_FILES | SHELL_MODULES
    if not required.issubset(paths):
        raise SetupError("tracked runtime files are missing")
    contents = {}
    for name in sorted(paths):
        original = safe_path(str(source / name))
        if not original.is_file():
            raise SetupError("runtime source must contain only regular files")
        # Read immutable commit objects, excluding ignored/untracked files and
        # defeating working-tree changes between the clean check and the copy.
        data = git(source, "show", f"{revision}:{name}")
        if original.read_bytes() != data:
            raise SetupError("runtime source differs from pinned commit")
        installed = "libexec/agent-dotfiles" if name == "bin/agent-dotfiles" else name
        contents[installed] = (data, 0o644)
    contents["bin/agent-dotfiles"] = (LAUNCHER, 0o755)
    manifest = {"schema": SCHEMA, "source_revision": revision,
                "files": {name: {"sha256": digest(data), "mode": mode}
                          for name, (data, mode) in sorted(contents.items())}}
    if preview:
        # Resolve the exact candidate bytes first, without creating a prefix.
        # A later install must repeat all checks against its approved SHA.
        return {"source_revision": revision, "files": len(contents), "entries": manifest["files"]}
    staging = Path(tempfile.mkdtemp(prefix=".agent-dotfiles-install-", dir=prefix.parent))
    try:
        for name, (data, mode) in contents.items():
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            target.chmod(mode)
        (staging / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        verify(staging)
        safe_path(str(prefix))
        if prefix.exists() and (not prefix.is_dir() or any(prefix.iterdir())):
            raise SetupError("prefix changed during installation")
        os.rename(staging, prefix)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return {"source_revision": revision, "files": len(contents)}


def verify(prefix: Path) -> dict:
    if not prefix.is_dir():
        raise SetupError("installation prefix is missing")
    manifest_path = prefix / MANIFEST
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise SetupError("regular installation manifest is required")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (not isinstance(manifest, dict) or set(manifest) != {"schema", "source_revision", "files"}
            or manifest["schema"] != SCHEMA
            or not isinstance(manifest["source_revision"], str)
            or not re.fullmatch(r"[0-9a-f]{40}", manifest["source_revision"])
            or not isinstance(manifest["files"], dict)):
        raise SetupError("unknown or invalid installation manifest")
    files = manifest["files"]
    required = {"LICENSE", "libexec/agent-dotfiles", "bin/agent-dotfiles",
                "agent_dotfiles/__init__.py", "agent_dotfiles/cli.py"}
    if not required.issubset(files):
        raise SetupError("incomplete installation manifest")
    if set(files) & SHELL_FILES and not SHELL_FILES.issubset(files):
        raise SetupError("incomplete shell profile manifest")
    # Existing v0.4.0 manifests have no modules and remain verifiable.
    if set(files) & SHELL_MODULES and (not SHELL_MODULES.issubset(files) or not SHELL_FILES.issubset(files)):
        raise SetupError("incomplete shell module manifest")
    directories = set()
    for name, entry in files.items():
        if name not in required | SHELL_FILES | SHELL_MODULES and not runtime_path(name):
            raise SetupError("unsafe or unknown installation entry")
        if (not isinstance(entry, dict) or set(entry) != {"sha256", "mode"}
                or not isinstance(entry["sha256"], str)
                or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])
                or entry["mode"] != (0o755 if name == "bin/agent-dotfiles" else 0o644)):
            raise SetupError("invalid installation file metadata")
        target = safe_path(str(prefix / name))
        if (not target.is_file() or digest(target.read_bytes()) != entry["sha256"]
                or stat.S_IMODE(target.stat().st_mode) != entry["mode"]):
            raise SetupError(f"installed file changed or missing: {name}")
        directories.update(str(parent) for parent in PurePosixPath(name).parents if str(parent) != ".")
    if files["bin/agent-dotfiles"]["sha256"] != digest(LAUNCHER):
        raise SetupError("unknown installation launcher")
    expected = set(files) | directories | {MANIFEST}
    actual = set()
    for base, dirs, names in os.walk(prefix, followlinks=False):
        for name in dirs + names:
            target = Path(base) / name
            if target.is_symlink():
                raise SetupError("symlink found in installation")
            actual.add(target.relative_to(prefix).as_posix())
    if actual != expected:
        raise SetupError("installation contains unknown or missing entries")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("install", "plan", "verify", "uninstall"):
        command = commands.add_parser(name, allow_abbrev=False)
        command.add_argument("--prefix", required=True)
        command.add_argument("--revision", required=name in ("install", "plan"),
                             help="full source commit; optionally assert the installed pin")
        if name in ("install", "plan"):
            command.add_argument("--source", required=True)
    args = parser.parse_args()
    try:
        prefix = safe_path(args.prefix)
        if args.command in ("install", "plan"):
            result = install(safe_path(args.source), args.revision, prefix,
                             preview=args.command == "plan")
        else:
            manifest = verify(prefix)
            if args.revision is not None and args.revision != manifest["source_revision"]:
                raise SetupError("installation does not match the expected pinned revision")
            result = {"source_revision": manifest["source_revision"], "files": len(manifest["files"])}
            if args.command == "uninstall":
                shutil.rmtree(prefix)
        print(json.dumps({"schema": SCHEMA, "operation": args.command, "ok": True, **result}))
        return 0
    except (SetupError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({"schema": SCHEMA, "operation": args.command, "ok": False, "error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
