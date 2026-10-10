"""Quality-first black-box checks against real Git, not mocked output.

Correct file identity and complete evidence are prerequisites for any A/B token
measurement: shorter output must not mean silently wrong or omitted context.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "bin" / "agent-dotfiles"
GIT = shutil.which("git")


@unittest.skipUnless(GIT, "Git needed for native oracle")
class GitPatchEvidenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Quality Test")
        self.git("config", "user.email", "test@example.invalid")

    def git(self, *args: str) -> bytes:
        return subprocess.run([GIT, *args], cwd=self.root, check=True,
                              capture_output=True, timeout=10).stdout

    def commit(self) -> None:
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")

    def cli(self, *args: str) -> tuple[int, dict]:
        r = subprocess.run([sys.executable, str(CLI), *args, "--root", str(self.root)],
                           cwd=self.root, text=True, capture_output=True,
                           check=False, timeout=15)
        self.assertEqual(r.stderr, "", r.stderr)
        return r.returncode, json.loads(r.stdout)

    def test_literal_filename_does_not_capture_unrelated_diff(self) -> None:
        for name in ("a[1].php", "a1.php", "a*.php"):
            (self.root / name).write_text("old " + name + "\n", encoding="utf-8")
        self.commit()
        for name in ("a[1].php", "a1.php", "a*.php"):
            (self.root / name).write_text("new " + name + "\n", encoding="utf-8")
        for name in ("a[1].php", "a*.php"):
            with self.subTest(filename=name):
                code, report = self.cli("git-patch", name)
                self.assertEqual(code, 0)
                native = subprocess.run(
                    [GIT, "diff", "--no-ext-diff", "--no-textconv",
                     "--no-color", "--binary", "--full-index", "--", name],
                    cwd=self.root, capture_output=True, check=True, timeout=10,
                    env={"PATH": str(Path(GIT).parent), "GIT_LITERAL_PATHSPECS": "1"},
                ).stdout
                self.assertEqual(report["patch"], {"text": native.decode("utf-8")})
                self.assertEqual(report["sha256"], hashlib.sha256(native).hexdigest())
                self.assertNotIn("new a1.php", report["patch"]["text"])
                self.assertFalse(report["truncated"])

    def test_subdirectory_root_preserves_exact_native_patch(self) -> None:
        (self.root / "src").mkdir()
        source = self.root / "src" / "a[1].php"
        source.write_text("before\n")
        self.commit()
        source.write_text("after\n")
        result = subprocess.run(
            [sys.executable, str(CLI), "git-patch", "a[1].php", "--root", str(source.parent)],
            capture_output=True, text=True, check=False, timeout=15,
        )
        self.assertEqual(0, result.returncode, result.stdout)
        evidence = json.loads(result.stdout)
        native = subprocess.run(
            [GIT, "diff", "--no-ext-diff", "--no-textconv", "--no-color", "--binary",
             "--full-index", "--", "a[1].php"], cwd=source.parent, capture_output=True,
            check=True, timeout=10, env={"GIT_LITERAL_PATHSPECS": "1"},
        ).stdout
        self.assertEqual({"text": native.decode()}, evidence["patch"])
        self.assertEqual(hashlib.sha256(native).hexdigest(), evidence["sha256"])
        self.assertEqual("a[1].php", evidence["path"])

    def test_untracked_file_does_not_look_like_clean_diff(self) -> None:
        (self.root / "tracked.php").write_text("tracked\n")
        self.commit()
        (self.root / "new.php").write_text("critical new code\n")
        code, evidence = self.cli("git-patch", "new.php")
        self.assertEqual(code, 2)
        self.assertEqual(evidence["error"], "path_not_in_diff")
        self.assertNotIn("patch", evidence)
        read_code, source = self.cli("read", "new.php")
        self.assertEqual(read_code, 0)
        self.assertEqual(source["content"], "critical new code\n")

    def test_ignored_file_does_not_look_like_clean_diff(self) -> None:
        (self.root / ".gitignore").write_text("generated.php\n")
        self.commit()
        (self.root / "generated.php").write_text("important ignored content\n")
        code, evidence = self.cli("git-patch", "generated.php")
        self.assertEqual(code, 2)
        self.assertEqual(evidence["error"], "path_not_in_diff")
        self.assertNotIn("patch", evidence)

    def test_unchanged_indexed_file_is_genuinely_empty(self) -> None:
        (self.root / "clean.php").write_text("same\n")
        self.commit()
        code, evidence = self.cli("git-patch", "clean.php")
        self.assertEqual(code, 0)
        self.assertEqual(evidence["patch"], {"text": ""})
        self.assertEqual(evidence["bytes"], 0)
        self.assertFalse(evidence["truncated"])

    def test_deleted_tracked_file_is_still_visible(self) -> None:
        (self.root / "deleted.php").write_text("old code\n")
        self.commit()
        (self.root / "deleted.php").unlink()
        code, evidence = self.cli("git-patch", "deleted.php")
        self.assertEqual(code, 0)
        self.assertIn("deleted file mode", evidence["patch"]["text"])
        self.assertIn("-old code", evidence["patch"]["text"])

    def test_existing_directory_is_not_a_file(self) -> None:
        (self.root / "src").mkdir()
        (self.root / "src" / "a.php").write_text("before\n")
        self.commit()
        (self.root / "src" / "a.php").write_text("after\n")
        code, evidence = self.cli("git-patch", "src")
        self.assertEqual(code, 2)
        self.assertEqual(evidence["error"], "invalid_file")

    def test_removed_directory_does_not_expand_to_many_files(self) -> None:
        folder = self.root / "gone"
        folder.mkdir()
        (folder / "a.php").write_text("a\n")
        (folder / "b.php").write_text("b\n")
        self.commit()
        (folder / "a.php").unlink()
        (folder / "b.php").unlink()
        folder.rmdir()
        code, evidence = self.cli("git-patch", "gone")
        self.assertEqual(code, 2)
        self.assertEqual(evidence["error"], "ambiguous_path")
        self.assertNotIn("patch", evidence)

    def test_staged_new_file_is_not_lost(self) -> None:
        (self.root / "base.txt").write_text("base\n")
        self.commit()
        (self.root / "new.php").write_text("staged code\n")
        self.git("add", "new.php")
        code, evidence = self.cli("git-patch", "new.php", "--staged")
        self.assertEqual(code, 0)
        self.assertIn("+staged code", evidence["patch"]["text"])


if __name__ == "__main__":
    unittest.main()
