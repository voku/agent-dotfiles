"""Repository versus installed-payload ownership regression checks."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest

from tools.install import installation_path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryOwnershipTest(unittest.TestCase):
    def test_durable_learning_is_not_consumer_payload(self) -> None:
        for name in (
            "MEMORY.md",
            "docs/REPOSITORY_LAYOUT.md",
            "docs/STEADY_STATE_EVALUATION.md",
            "docs/decisions/0001-product-boundaries.md",
            ".agent-loop/init.json",
            ".agent-loop/learning/config.json",
            "tools/install.py",
            "tests/test_repository_ownership.py",
            "examples/gitconfig.agent.example",
        ):
            with self.subTest(path=name):
                self.assertTrue((ROOT / name).is_file(), name)
                self.assertFalse(installation_path(name), name)

    def test_runtime_inputs_remain_explicit(self) -> None:
        for name in (
            ".bashrc",
            ".zshrc",
            ".shellrc",
            ".exports",
            ".functions",
            "shell/modules/context.sh",
            "shell/modules/git.sh",
            "profiles/minimal.json",
        ):
            with self.subTest(path=name):
                self.assertTrue(installation_path(name), name)

    def test_project_learning_root_uses_upstream_shape(self) -> None:
        init = json.loads((ROOT / ".agent-loop/init.json").read_text(encoding="utf-8"))
        config = json.loads(
            (ROOT / ".agent-loop/learning/config.json").read_text(encoding="utf-8")
        )
        self.assertEqual(init["version"], 1)
        self.assertEqual(init["paths"]["learning_root"], ".agent-loop/learning")
        self.assertEqual(config["schema_version"], "1.0")
        self.assertEqual(config["project_root"], "../..")
        self.assertTrue(
            (ROOT / ".agent-loop/learning/findings/validated").is_dir()
        )

    def test_raw_learning_data_not_allowlisted_for_git(self) -> None:
        rules = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("/.agent-loop/*", rules)
        self.assertIn("!/.agent-loop/init.json", rules)
        self.assertIn("!/.agent-loop/learning/config.json", rules)
        self.assertIn("!/.agent-loop/learning/findings/validated/*.json", rules)
        self.assertIn("/.agent-loop/learning/history/", rules)

    def test_git_excludes_raw_state_but_allows_reviewed_findings(self) -> None:
        cases = {
            ".agent-loop/private-session.json": True,
            ".agent-loop/learning/history/session.json": True,
            ".agent-loop/learning/notes/unreviewed.json": True,
            ".agent-loop/learning/findings/consolidated/unreviewed.json": True,
            ".agent-loop/init.json": False,
            ".agent-loop/learning/config.json": False,
            ".agent-loop/learning/findings/validated/finding.test.json": False,
        }
        for path, ignored in cases.items():
            with self.subTest(path=path):
                result = subprocess.run(
                    ["git", "-C", str(ROOT), "check-ignore", "--no-index",
                     "--quiet", "--", path],
                    capture_output=True,
                    check=False,
                    timeout=10,
                )
                self.assertIn(result.returncode, (0, 1), result.stderr)
                self.assertEqual(result.returncode == 0, ignored, path)


if __name__ == "__main__":
    unittest.main()
