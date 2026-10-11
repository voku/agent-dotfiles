"""Real Git workspace identity contracts. No network or shell startup files."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from agent_dotfiles import cli as cli_module
from agent_dotfiles.validation import CommandFailure

PROJECT = Path(__file__).resolve().parent.parent
CLI = PROJECT / "bin" / "agent-dotfiles"


class WorkspaceTest(unittest.TestCase):
    def setUp(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("Git is required for workspace integration tests")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / "checkout space [雪]\n"
        self.repo.mkdir()
        self.git("init", "-q")
        (self.repo / "tracked.txt").write_text("initial\n", encoding="utf-8")
        self.git("add", "tracked.txt")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "initial")

    def git(self, *args: str, cwd: Path | None = None) -> str:
        completed = subprocess.run(["git", *args], cwd=cwd or self.repo,
                                   capture_output=True, text=True, check=True, timeout=10)
        return completed.stdout.strip()

    def workspace(self, *args: str) -> tuple[int, dict[str, object]]:
        completed = subprocess.run([sys.executable, str(CLI), "workspace",
                                    "--root", str(self.repo), *args],
                                   cwd=self.root, capture_output=True, text=True,
                                   env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
                                   check=False, timeout=20)
        self.assertEqual(completed.stderr, "", completed.stderr)
        return completed.returncode, json.loads(completed.stdout)

    def test_clean_checkout_and_subdirectory(self) -> None:
        nested = self.repo / "src"
        nested.mkdir()
        code, report = self.workspace("--root", str(nested))
        self.assertEqual(code, 0, report)
        self.assertEqual(report["schema"], "agent-dotfiles.v1.workspace")
        self.assertEqual(report["root"], str(self.repo))
        self.assertEqual(report["requested_root"], str(nested))
        self.assertEqual(report["head"], self.git("rev-parse", "HEAD"))
        self.assertEqual(report["branch"], self.git("branch", "--show-current"))
        self.assertFalse(report["detached"])
        self.assertTrue(report["clean"])
        self.assertEqual(report["changes"], [])
        self.assertFalse(report["truncated"])
        self.assertTrue(report["head_unchanged_during_probe"])
        self.assertFalse(report["worktree_atomic"])
        self.assertFalse((self.repo / ".git/index.lock").exists())

    def test_staged_unstaged_untracked_and_detached(self) -> None:
        (self.repo / "staged.txt").write_text("staged", encoding="utf-8")
        self.git("add", "staged.txt")
        (self.repo / "tracked.txt").write_text("modified", encoding="utf-8")
        (self.repo / "new\nname.txt").write_text("new", encoding="utf-8")
        code, report = self.workspace()
        self.assertEqual(code, 0, report)
        self.assertFalse(report["clean"])
        self.assertEqual({(entry["xy"], entry["path"]) for entry in report["changes"]},
                         {("A ", "staged.txt"), (" M", "tracked.txt"), ("??", "new\nname.txt")})
        self.git("checkout", "-q", "--detach", "HEAD")
        code, detached = self.workspace()
        self.assertEqual(code, 0, detached)
        self.assertIsNone(detached["branch"])
        self.assertTrue(detached["detached"])
        self.assertEqual(detached["head"], report["head"])

    def test_truncation_never_claims_clean_or_complete(self) -> None:
        (self.repo / "one.txt").write_text("one", encoding="utf-8")
        (self.repo / "two.txt").write_text("two", encoding="utf-8")
        code, report = self.workspace("--limit", "1")
        self.assertEqual(code, 3, report)
        self.assertTrue(report["truncated"])
        self.assertIsNone(report["clean"])
        self.assertEqual(len(report["changes"]), 1)

    def test_git_rename_keeps_original_path_and_bounded_record(self) -> None:
        renamed = "renamed [雪]\\n.txt"
        self.git("mv", "tracked.txt", renamed)
        code, report = self.workspace("--limit", "1")
        self.assertEqual(code, 0, report)
        self.assertFalse(report["clean"])
        self.assertFalse(report["truncated"])
        self.assertEqual(report["changes"],
                         [{"xy": "R ", "path": renamed, "original_path": "tracked.txt"}])

        (self.repo / "additional.txt").write_text("untracked", encoding="utf-8")
        code, limited = self.workspace("--limit", "1")
        self.assertEqual(code, 3, limited)
        self.assertTrue(limited["truncated"])
        self.assertIsNone(limited["clean"])
        self.assertEqual(len(limited["changes"]), 1)
        self.assertEqual(limited["changes"][0]["original_path"], "tracked.txt")

    def test_linked_git_worktree_resolves_its_own_root(self) -> None:
        linked = self.root / "linked worktree [雪]"
        self.git("worktree", "add", "-q", "--detach", str(linked), "HEAD")
        self.assertTrue((linked / ".git").is_file())
        nested = linked / "nested"
        nested.mkdir()
        (linked / "only-in-worktree.txt").write_text("untracked", encoding="utf-8")
        code, report = self.workspace("--root", str(nested))
        self.assertEqual(code, 0, report)
        self.assertEqual(report["root"], str(linked.resolve()))
        self.assertEqual(report["requested_root"], str(nested.resolve()))
        self.assertEqual(report["head"], self.git("rev-parse", "HEAD"))
        self.assertIsNone(report["branch"])
        self.assertTrue(report["detached"])
        self.assertEqual(report["changes"],
                         [{"xy": "??", "path": "only-in-worktree.txt"}])
        self.assertFalse(report["clean"])

    def test_identity_changes_during_status_refuse_snapshot(self) -> None:
        original = cli_module._git_status_command

        def change_branch_during_status(args: argparse.Namespace):
            result = original(args)
            # Real Git operation between the two identity probes, not a
            # mocked or fabricated identity response.
            self.git("checkout", "-q", "--detach", "HEAD")
            return result

        with mock.patch.object(cli_module, "_git_status_command",
                               side_effect=change_branch_during_status):
            with self.assertRaises(CommandFailure) as failure:
                cli_module._workspace_command(argparse.Namespace(
                    root=str(self.repo), limit=100))
        self.assertEqual(failure.exception.reason, "snapshot_changed")

    def test_outside_checkout_and_unborn_head_fail_explicitly(self) -> None:
        plain = self.root / "plain"
        plain.mkdir()
        code, report = self.workspace("--root", str(plain))
        self.assertEqual(code, 2)
        self.assertEqual(report["schema"], "agent-dotfiles.v1.error")
        self.assertEqual(report["error"], "tool_failed")
        unborn = self.root / "unborn"
        unborn.mkdir()
        self.git("init", "-q", cwd=unborn)
        code, report = self.workspace("--root", str(unborn))
        self.assertEqual(code, 2)
        self.assertEqual(report["error"], "tool_failed")


if __name__ == "__main__":
    unittest.main()
