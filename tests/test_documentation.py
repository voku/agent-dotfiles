"""Public-documentation contracts that do not require third-party packages."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DOCUMENTS = (
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "CONTRIBUTING.md",
    PROJECT_ROOT / "CODE_OF_CONDUCT.md",
    PROJECT_ROOT / "SUPPORT.md",
    PROJECT_ROOT / "docs" / "README.md",
    PROJECT_ROOT / "docs" / "AGENT_SKILLS.md",
    PROJECT_ROOT / "docs" / "SECURITY.md",
    PROJECT_ROOT / "docs" / "CLI.md",
    PROJECT_ROOT / "prompts" / "setup-project.md",
)
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)\s]+)(?:\s+[^)]*)?\)")
EXTERNAL_SCHEMES = ("https:", "http:", "mailto:")


class PublicDocumentationTest(unittest.TestCase):
    def test_public_documents_exist(self) -> None:
        for document in PUBLIC_DOCUMENTS:
            self.assertTrue(document.is_file(), document)

    def test_local_markdown_links_resolve(self) -> None:
        for document in PUBLIC_DOCUMENTS:
            for match in MARKDOWN_LINK.finditer(document.read_text(encoding="utf-8")):
                target = match.group(1).strip("<>")
                local_target = target.split("#", 1)[0]
                if not local_target or local_target.startswith(EXTERNAL_SCHEMES):
                    continue
                self.assertTrue(
                    (document.parent / local_target).is_file(),
                    f"{document.relative_to(PROJECT_ROOT)} links to missing {target}",
                )

    def test_readme_keeps_the_safe_entry_points_visible(self) -> None:
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        for expected in (
            "doctor --profile minimal",
            "firstInstall.sh plan",
            "docs/FIRST_INSTALL.md",
            "docs/INSTALLATION.md",
            "CONTRIBUTING.md",
            "docs/SECURITY.md",
        ):
            self.assertIn(expected, readme)

    def test_readme_checkout_commands_work_in_isolated_git_project(self) -> None:
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("./firstInstall.sh plan", readme)
        self.assertIn("./bin/agent-dotfiles doctor --profile minimal", readme)
        self.assertIn(
            "./bin/agent-dotfiles workspace --root /absolute/path/to/project --limit 50",
            readme,
        )
        with tempfile.TemporaryDirectory(prefix="onboarding repo λ ") as tmp:
            root = Path(tmp) / "fresh project"
            root.mkdir()
            env = os.environ.copy()
            for inherited in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "BASH_ENV"):
                env.pop(inherited, None)
            env["GIT_OPTIONAL_LOCKS"] = "0"
            init = subprocess.run(
                ["git", "init", "-q", str(root)],
                capture_output=True, text=True, timeout=20, env=env, check=False,
            )
            self.assertEqual(init.returncode, 0, init.stderr)
            baseline = subprocess.run(
                ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"],
                capture_output=True, text=True, timeout=20, env=env, check=False,
            )
            self.assertEqual(baseline.returncode, 0, baseline.stderr)
            unborn = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "bin" / "agent-dotfiles"),
                 "workspace", "--root", str(root), "--limit", "50"],
                capture_output=True, text=True, timeout=20, env=env, check=False,
            )
            self.assertEqual(unborn.returncode, 2, unborn.stdout + unborn.stderr)
            self.assertEqual(json.loads(unborn.stdout)["error"], "missing_head")
            (root / "tracked.txt").write_text("hello, real checkout\\n", encoding="utf-8")
            added = subprocess.run(
                ["git", "-C", str(root), "add", "--", "tracked.txt"],
                capture_output=True, text=True, timeout=20, env=env, check=False,
            )
            self.assertEqual(added.returncode, 0, added.stderr)
            committed = subprocess.run(
                ["git", "-C", str(root), "-c", "user.name=Fixture",
                 "-c", "user.email=fixture@example.invalid", "commit", "-qm", "initial"],
                capture_output=True, text=True, timeout=20, env=env, check=False,
            )
            self.assertEqual(committed.returncode, 0, committed.stderr)
            baseline = subprocess.run(
                ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"],
                capture_output=True, text=True, timeout=20, env=env, check=False,
            )
            self.assertEqual(baseline.returncode, 0, baseline.stderr)
            self.assertEqual(baseline.stdout, "")
            doctor = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "bin" / "agent-dotfiles"),
                 "doctor", "--profile", "minimal"],
                capture_output=True, text=True, timeout=20, env=env, check=False,
            )
            self.assertEqual(doctor.returncode, 0, doctor.stderr)
            self.assertEqual(json.loads(doctor.stdout)["schema"], "agent-dotfiles.v1.doctor")
            workspace = subprocess.run(
                [sys.executable, str(PROJECT_ROOT / "bin" / "agent-dotfiles"),
                 "workspace", "--root", str(root), "--limit", "50"],
                capture_output=True, text=True, timeout=20, env=env, check=False,
            )
            self.assertEqual(workspace.returncode, 0, workspace.stderr)
            report = json.loads(workspace.stdout)
            self.assertEqual(report["schema"], "agent-dotfiles.v1.workspace")
            self.assertEqual(Path(report["root"]), root.resolve())
            status = subprocess.run(
                ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"],
                capture_output=True, text=True, timeout=20, env=env, check=False,
            )
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertEqual(status.stdout, baseline.stdout)
            self.assertFalse((root / ".agent-loop").exists())
            self.assertFalse((root / "MEMORY.md").exists())

    def test_guarded_manual_skill_projection_for_codex_and_claude(self) -> None:
        instructions = (PROJECT_ROOT / "docs" / "PROJECT_ONBOARDING.md").read_text(
            encoding="utf-8"
        )
        self.assertIn('test ! -e "$skill_target"', instructions)
        self.assertIn('cp -R "$skill_source" "$skill_target"', instructions)
        source = PROJECT_ROOT / "skills" / "project-onboarding"
        script = (
            "set -eu; "
            'skill_source="$1"; skill_target="$2"; '
            'test ! -e "$skill_target" || { echo "refusing existing skill" >&2; exit 2; }; '
            'mkdir -p "${skill_target%/*}"; '
            'cp -R "$skill_source" "$skill_target"; '
            'cmp -s "$skill_source/SKILL.md" "$skill_target/SKILL.md"'
        )
        with tempfile.TemporaryDirectory(prefix="onboarding skill λ ") as tmp:
            project = Path(tmp) / "fresh project"
            project.mkdir()
            for host in (".codex", ".claude"):
                target = project / host / "skills" / "project-onboarding"
                cmd = ["sh", "-c", script, "project-onboarding", str(source), str(target)]
                first = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=20, check=False,
                )
                self.assertEqual(first.returncode, 0, first.stderr)
                self.assertEqual(
                    (target / "SKILL.md").read_bytes(),
                    (source / "SKILL.md").read_bytes(),
                )
                (target / "SKILL.md").write_text("local override", encoding="utf-8")
                repeated = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=20, check=False,
                )
                self.assertEqual(repeated.returncode, 2, repeated.stderr)
                self.assertEqual(
                    (target / "SKILL.md").read_text(encoding="utf-8"),
                    "local override",
                )
            self.assertFalse((project / ".agent-loop").exists())
            self.assertFalse((project / "MEMORY.md").exists())

    def test_setup_prompt_preserves_workflow_ownership(self) -> None:
        prompt = (PROJECT_ROOT / "prompts" / "setup-project.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Do not install or configure `agent-loop`", prompt)
        self.assertIn("project memory", prompt)
        self.assertIn("unavailable", prompt.lower())
        self.assertIn("CODEX", prompt.upper())
        self.assertIn("CLAUDE", prompt.upper())

    def test_skill_sync_docs_keep_replace_as_an_explicit_review_step(self) -> None:
        skills_doc = (PROJECT_ROOT / "docs" / "AGENT_SKILLS.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("--replace --dry-run", skills_doc)
        self.assertIn("voku/agent-skills", skills_doc)
