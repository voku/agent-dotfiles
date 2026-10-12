"""Public-documentation contracts that do not require third-party packages."""

from __future__ import annotations

import re
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

    def test_skill_sync_docs_keep_replace_as_an_explicit_review_step(self) -> None:
        skills_doc = (PROJECT_ROOT / "docs" / "AGENT_SKILLS.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("--replace --dry-run", skills_doc)
        self.assertIn("voku/agent-skills", skills_doc)
