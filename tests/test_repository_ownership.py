"""Keep maintainer-only material out of the agent-dotfiles consumer payload."""

from __future__ import annotations

from pathlib import Path
import unittest

from tools.install import installation_path


ROOT = Path(__file__).resolve().parents[1]


class RepositoryOwnershipTest(unittest.TestCase):
    def test_maintainer_files_are_not_consumer_payload(self) -> None:
        for name in (
            "docs/REPOSITORY_LAYOUT.md",
            "docs/STEADY_STATE_EVALUATION.md",
            "docs/decisions/0001-product-boundaries.md",
            "tools/install.py",
            "tests/test_repository_ownership.py",
            "examples/gitconfig.agent.example",
        ):
            with self.subTest(path=name):
                self.assertTrue((ROOT / name).is_file(), name)
                self.assertFalse(installation_path(name), name)

    def test_workflow_and_memory_belong_to_independent_agent_loop(self) -> None:
        for name in (".agent-loop/init.json", "MEMORY.md", "docs/recall-documents.json"):
            with self.subTest(path=name):
                self.assertFalse((ROOT / name).exists(), name)
                self.assertFalse(installation_path(name), name)

    def test_git_example_path_is_copyable(self) -> None:
        example = (ROOT / "examples/gitconfig.agent.example").read_text(encoding="utf-8")
        self.assertIn("include.path=/absolute/path/examples/gitconfig.agent.example", example)
        self.assertNotIn("/absolute/path/config/gitconfig.agent.example", example)

    def test_runtime_inputs_remain_explicit(self) -> None:
        for name in (
            ".bashrc", ".zshrc", ".shellrc", ".exports", ".functions",
            "shell/modules/context.sh", "shell/modules/git.sh",
            "profiles/minimal.json",
        ):
            with self.subTest(path=name):
                self.assertTrue(installation_path(name), name)


if __name__ == "__main__":
    unittest.main()
