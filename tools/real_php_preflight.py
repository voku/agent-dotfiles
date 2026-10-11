#!/usr/bin/env python3
"""Unscored command-evidence preflight against a pinned real PHP repository.

This is not an LLM task comparison: it does not execute governed agents, score
maintenance fixes or infer token savings from command-output sizes.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any


PATTERN = "final readonly class InitToolsCommand"
SOURCE = "src/Init/InitToolsCommand.php"
START, END = 1, 8


def execute(
    argv: list[str], cwd: Path, trace: list[dict[str, Any]], *, expected: int = 0
) -> bytes:
    before = time.monotonic_ns()
    environment = os.environ.copy()
    environment.pop("BASH_ENV", None)
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    environment["GIT_PAGER"] = "cat"
    environment["NO_COLOR"] = "1"
    environment["RIPGREP_CONFIG_PATH"] = os.devnull
    result = subprocess.run(
        argv, cwd=cwd, env=environment, capture_output=True, timeout=40, check=False
    )
    trace.append(
        {
            "argv": argv,
            "exit": result.returncode,
            "elapsed_ns": time.monotonic_ns() - before,
            "stdout_bytes": len(result.stdout),
            "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
            "stderr_bytes": len(result.stderr),
            "stderr_sha256": hashlib.sha256(result.stderr).hexdigest(),
        }
    )
    if result.returncode != expected:
        raise RuntimeError(
            f"command returned {result.returncode}, expected {expected}: "
            f"{argv!r}; stderr={result.stderr[:800]!r}"
        )
    return result.stdout


def json_object(raw: bytes) -> dict[str, Any]:
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value


def check_search(raw: bytes, oracle: list[dict[str, Any]]) -> None:
    value = json_object(raw)
    if (
        value.get("schema") != "agent-dotfiles.v1.search"
        or value.get("truncated") is not False
        or value.get("matches") != oracle
    ):
        raise AssertionError("Search results differ from the native full rg --json oracle")


def check_read(raw: bytes, original: bytes) -> None:
    value = json_object(raw)
    text = original.decode("utf-8")
    lines = text.split("\n")
    expected = [s + "\n" for s in lines[:-1]]
    if lines[-1]:
        expected.append(lines[-1])
    selected = "".join(expected[START - 1:END])
    if (
        value.get("schema") != "agent-dotfiles.v1.read"
        or value.get("truncated") is not False
        or value.get("start") != START
        or value.get("actual_end") != min(END, len(expected))
        or value.get("sha256") != hashlib.sha256(original).hexdigest()
        or value.get("content") != selected
        or value.get("content_bytes") != len(selected.encode("utf-8"))
    ):
        raise AssertionError("Read bytes, line coordinates or full-file hash differ from original")


def shell_call(
    name: str, dotfiles: Path, command: str, args: list[str]
) -> list[str]:
    shell = shutil.which(name)
    if shell is None:
        raise RuntimeError(f"Required shell missing: {name}")
    flags = ["--noprofile", "--norc"] if name == "bash" else ["-f"]
    script = '. "$1" || exit $?; shift; "$@"'
    profile = str(dotfiles / (".bashrc" if name == "bash" else ".zshrc"))
    return [shell, *flags, "-c", script, "preflight", profile, command, *args]


def main() -> int:
    dotfiles = Path(os.environ["DOTFILES_CHECKOUT"]).resolve(strict=True)
    php_repo = Path(os.environ["PHP_CHECKOUT"]).resolve(strict=True)
    consumer = Path(os.environ["CONSUMER_PREFIX"]).resolve(strict=True)
    artifact = Path(os.environ["PREFLIGHT_RECEIPT"])
    trace: list[dict[str, Any]] = []
    report: dict[str, Any] = {
        "purpose": "unscored real-PHP command-evidence parity, not agent A/B/C effectiveness",
        "source": SOURCE,
        "needle": PATTERN,
        "expected_dotfiles_sha": os.environ["DOTFILES_SHA"],
        "expected_php_sha": os.environ["PHP_SHA"],
        "model_tokens": None,
        "installed_prefix": str(consumer),
        "trace": trace,
        "checks": [],
        "result": "fail",
    }
    try:
        for key, root in (("dotfiles", dotfiles), ("php", php_repo)):
            found = execute(["git", "rev-parse", "HEAD"], root, trace).decode().strip()
            report[key + "_sha"] = found
            if found != report["expected_" + key + "_sha"]:
                raise AssertionError(f"Checkout revision mismatch: {key}")

        for tool in ("python3", "git", "rg", "bash", "zsh"):
            resolved = shutil.which(tool)
            if resolved is None:
                raise RuntimeError(f"Missing preflight tool: {tool}")
            report.setdefault("tools", {})[tool] = resolved

        source = (php_repo / SOURCE).read_bytes()
        report["source_sha256"] = hashlib.sha256(source).hexdigest()
        native = execute(
            ["rg", "--json", "--color=never", "--no-heading", "--fixed-strings",
             "--", PATTERN, SOURCE], php_repo, trace
        )
        oracle = [
            event["data"]
            for event in (json.loads(line) for line in native.splitlines())
            if event.get("type") == "match"
        ]
        if len(oracle) != 1 or oracle[0].get("line_number") is None:
            raise AssertionError("The pinned PHP literal search oracle changed")
        report["oracle_match_count"] = len(oracle)
        report["checks"].append("native-literal-oracle")

        binary = str(consumer / "bin/agent-dotfiles")
        doctor = json_object(execute([binary, "doctor"], consumer, trace))
        if doctor.get("schema") != "agent-dotfiles.v1.doctor" or doctor.get("missing_required"):
            raise AssertionError("Installed candidate doctor reported missing requirements")
        report["installed_version"] = doctor.get("version")
        report["checks"].append("installed-cli-doctor")
        search_args = ["search", PATTERN, "--root", str(php_repo),
                       "--path", SOURCE, "--limit", "10"]
        read_args = ["read", SOURCE, "--root", str(php_repo),
                     "--start", str(START), "--end", str(END)]
        check_search(execute([binary, *search_args], dotfiles, trace), oracle)
        check_read(execute([binary, *read_args], dotfiles, trace), source)
        report["checks"].append("direct-cli-search-and-read")

        for name in ("bash", "zsh"):
            search = shell_call(name, consumer, "agent_search", search_args[1:])
            read = shell_call(name, consumer, "agent_read", read_args[1:])
            check_search(execute(search, dotfiles, trace), oracle)
            check_read(execute(read, dotfiles, trace), source)
            report["checks"].append(name + "-fresh-shell-search-and-read")

        native_status = execute(
            ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
            php_repo, trace
        )
        if native_status:
            raise AssertionError("Pinned PHP checkout is not clean")
        status = json_object(
            execute([binary, "git-status", "--root", str(php_repo)], dotfiles, trace)
        )
        if status.get("truncated") is not False or status.get("changes") != []:
            raise AssertionError("CLI status disagrees with clean native Git checkout")
        report["checks"].append("clean-native-git-versus-cli-status")
        report["result"] = "pass"
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n")
    print(json.dumps({"result": report["result"], "checks": report["checks"],
                      "receipt": str(artifact), "error": report.get("error")}))
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
