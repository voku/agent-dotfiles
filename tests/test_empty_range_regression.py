"""Real consumer finding: nonexistent empty-file ranges cannot be evidence."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / "bin/agent-dotfiles"


class EmptyRangeRegression(unittest.TestCase):
    def test_empty_file_rejects_noninitial_range(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "empty.txt").write_bytes(b"")
            result = subprocess.run(
                [sys.executable, str(CLI), "read", "empty.txt", "--root", directory,
                 "--start", "2", "--end", "3"], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertEqual(json.loads(result.stdout)["error"], "invalid_range")

    def test_empty_file_initial_range_remains_complete(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "empty.txt").write_bytes(b"")
            result = subprocess.run(
                [sys.executable, str(CLI), "read", "empty.txt", "--root", directory,
                 "--start", "1", "--end", "1"], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["content"], "")
            self.assertEqual(report["sha256"], hashlib.sha256(b"").hexdigest())
            self.assertTrue(report["complete_file"])
            self.assertFalse(report["truncated"])
