"""Portable project-local skill layout and safety contracts."""
from pathlib import Path
import shutil
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[1]
SKILL = PROJECT / "skills/project-onboarding/SKILL.md"
TARGETS = {
    "codex": ".codex/skills/project-onboarding/SKILL.md",
    "claude": ".claude/skills/project-onboarding/SKILL.md",
}


class ProjectOnboardingSkillTest(unittest.TestCase):
    def test_skill_has_a_single_portable_contract(self):
        content = SKILL.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---\nname: project-onboarding\n"))
        for marker in ("git rev-parse --show-toplevel",
                       "git status --porcelain=v1 -z --untracked-files=all",
                       "canonical declared capability",
                       "agent-loop map", "VERIFIED:", "UNAVAILABLE", "INCOMPLETE"):
            self.assertIn(marker, content)
        self.assertIn("`composer test`, `composer ci`, `phpstan`, PHPUnit, or install/update", content)
        self.assertNotIn("composer run --list", content)
        for forbidden in ("composer install", "composer update", "eval ", "PATH="):
            self.assertNotIn(forbidden, content)

    def test_codex_and_claude_targets_receive_identical_reviewed_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for host, target in TARGETS.items():
                with self.subTest(host=host):
                    destination = root / host / target
                    destination.parent.mkdir(parents=True)
                    shutil.copyfile(SKILL, destination)
                    self.assertEqual(destination.read_bytes(), SKILL.read_bytes())
                    self.assertEqual(destination.relative_to(root / host).as_posix(), target)
            self.assertFalse((root / "codex/.claude").exists())
            self.assertFalse((root / "claude/.codex").exists())

    def test_documentation_forces_project_local_host_targets(self):
        documentation = (PROJECT / "docs/PROJECT_ONBOARDING.md").read_text()
        self.assertIn('CODEX_HOME="$PWD/.codex"', documentation)
        self.assertIn('CODEX_SKILLS_DIR="$PWD/.codex/skills"', documentation)
        self.assertIn('CLAUDE_SKILLS_DIR="$PWD/.claude/skills"', documentation)
        self.assertIn("init install-assets --agent=codex", documentation)
        self.assertIn("--extra-skills-root=/absolute/approved-agent-dotfiles-prefix/skills --skip-git-config --dry-run",
                      documentation)
        self.assertIn("--skip-git-config", documentation)
        self.assertNotIn("init sync-skills --agent=codex", documentation)
        self.assertNotIn("--skills-root=", documentation)


if __name__ == "__main__":
    unittest.main()
