"""Summarize Cosmic Ray without counting timeouts as successful test kills."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys


def summarize(path: Path) -> tuple[str, bool]:
    counts: Counter[str] = Counter()
    survivors: list[str] = []
    with path.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                item, result = json.loads(line)
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Invalid JSON at line {number}") from exc
            if not isinstance(item, dict) or not isinstance(item.get("mutations"), list):
                raise ValueError(f"Invalid work item at line {number}")
            if result is None:
                counts["pending"] += 1
                continue
            if not isinstance(result, dict):
                raise ValueError(f"Invalid result at line {number}")
            if result.get("worker_outcome") != "normal":
                counts["worker_error"] += 1
                continue
            outcome = result.get("test_outcome")
            if outcome == "survived":
                counts["survived"] += 1
                names = [
                    f"{m.get('module_path')}:{m.get('start_pos')} {m.get('operator_name')}"
                    for m in item["mutations"]
                ]
                survivors.append("; ".join(names))
            elif outcome == "killed":
                if "timeout" in (result.get("output") or "").lower():
                    counts["timeout"] += 1
                else:
                    counts["killed"] += 1
            else:
                counts["incompetent"] += 1
    total = sum(counts.values())
    if total == 0:
        raise ValueError("No mutants were generated")
    conclusive = counts["killed"] + counts["survived"]
    score = 100 * counts["killed"] / conclusive if conclusive else 0.0
    lines = [
        "## Targeted mutation experiment: validation.py",
        "",
        f"- Total work items: {total}",
        f"- Killed by test failure: {counts['killed']}",
        f"- Survived: {counts['survived']}",
        f"- Pending: {counts['pending']}",
        f"- Timeout (inconclusive): {counts['timeout']}",
        f"- Incompetent: {counts['incompetent']}",
        f"- Worker errors: {counts['worker_error']}",
        f"- Conclusive mutation kill rate: {score:.1f}%",
        "",
        "This is not a whole-repository score. Survivors require inspection;",
        "the experiment does not gate on an arbitrary percentage.",
    ]
    if survivors:
        lines.extend(["", "### Surviving mutants", ""])
        lines.extend("- " + name for name in survivors[:40])
    valid = not any(counts[k] for k in ("pending", "timeout", "incompetent", "worker_error"))
    return "\n".join(lines) + "\n", valid


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dump", type=Path)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()
    try:
        report, valid = summarize(args.dump)
    except (OSError, ValueError) as exc:
        print(f"Invalid mutation evidence: {exc}", file=sys.stderr)
        return 2
    args.markdown.write_text(report, encoding="utf-8")
    print(report)
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
