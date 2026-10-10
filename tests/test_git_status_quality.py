"""Real Git oracle: new files remain individually discoverable."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

GIT = shutil.which("git")
CLI = Path(__file__).resolve().parents[1] / "bin" / "agent-dotfiles"


@unittest.skipUnless(GIT, "Git binary required")
class GitStatusQualityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        subprocess.run([GIT, "init", "-q"], cwd=self.root, check=True, timeout=10)
        (self.root / "newdir").mkdir()
        for name in ("critical.php", "critical_test.php"):
            (self.root / "newdir" / name).write_text(name, encoding="utf-8")

    def cli(self, *args: str) -> tuple[int, dict]:
        result = subprocess.run(
            [sys.executable, str(CLI), "git-status", "--root", str(self.root), *args],
            cwd=self.root, text=True, capture_output=True, check=False, timeout=15,
        )
        self.assertEqual(result.stderr, "", result.stderr)
        return result.returncode, json.loads(result.stdout)

    def test_nested_untracked_paths_match_native_file_level_oracle(self) -> None:
        code, report = self.cli()
        self.assertEqual(code, 0)
        self.assertFalse(report["truncated"])
        native = subprocess.run(
            [GIT, "status", "--porcelain=v1", "-z", "--untracked-files=all"],
            cwd=self.root, capture_output=True, check=True, timeout=10,
        ).stdout
        expected = [item[3:].decode("utf-8") for item in native.split(b"\0") if item]
        actual = [item["path"] for item in report["changes"]]
        self.assertEqual(actual, expected)
        self.assertEqual(set(actual), {"newdir/critical.php", "newdir/critical_test.php"})

    def test_file_granularity_still_reports_bounded_truncation(self) -> None:
        code, report = self.cli("--limit", "1")
        self.assertEqual(code, 3)
        self.assertEqual(len(report["changes"]), 1)
        self.assertTrue(report["truncated"])
        self.assertIn(report["changes"][0]["path"],
                      {"newdir/critical.php", "newdir/critical_test.php"})


if __name__ == "__main__":
    unittest.main()
