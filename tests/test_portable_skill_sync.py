"""Contracts for explicit, local portable-skill synchronization."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[1]
SYNC = PROJECT / "tools/sync_portable_skills.py"
SKILLS = (
    "coding-simplicity",
    "testing-best-practices",
    "php-static-analysis",
    "language-onboarding-authoring",
)


class PortableSkillSyncTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "agent-skills"
        self.destination = self.root / "agent-dotfiles"
        self.source.mkdir()
        self.destination.mkdir()
        for skill in SKILLS:
            directory = self.source / "skills" / skill
            directory.mkdir(parents=True)
            (directory / "SKILL.md").write_text(
                f"---\nname: {skill}\ndescription: fixture\n---\n\n# Fixture\n",
                encoding="utf-8",
            )
        (self.source / "skills/testing-best-practices/rules").mkdir()
        (self.source / "skills/testing-best-practices/rules/example.md").write_text("fixture\n")
        unselected = self.source / "skills/unselected"
        unselected.mkdir()
        (unselected / "SKILL.md").write_text("unselected\n")
        self.git("init", "-q")
        self.git("remote", "add", "origin", "https://github.com/voku/agent-skills.git")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "fixture")
        self.revision = self.git("rev-parse", "HEAD").strip()

    def git(self, *arguments):
        return subprocess.check_output(["git", "-C", str(self.source), *arguments], text=True)

    def sync(self, *arguments):
        result = subprocess.run(
            [sys.executable, str(SYNC), "--source", str(self.source),
             "--revision", self.revision, "--destination", str(self.destination), *arguments],
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.stderr, "", result.stderr)
        return result.returncode, json.loads(result.stdout)

    def test_sync_copies_only_selected_skills_and_records_digests(self):
        status, report = self.sync("--dry-run")
        self.assertEqual(status, 0, report)
        self.assertFalse((self.destination / "skills").exists())
        status, report = self.sync()
        self.assertEqual(status, 0, report)
        self.assertEqual(report["skills"], list(SKILLS))
        self.assertTrue((self.destination / "skills/testing-best-practices/rules/example.md").is_file())
        self.assertFalse((self.destination / "skills/unselected").exists())
        manifest = json.loads((self.destination / "skills/portable-skills.json").read_text())
        self.assertEqual(manifest["source"], {"repository": "voku/agent-skills", "revision": self.revision})
        copied = (self.destination / "skills/coding-simplicity/SKILL.md").read_bytes()
        self.assertEqual(manifest["skills"]["coding-simplicity"]["files"]["SKILL.md"],
                         hashlib.sha256(copied).hexdigest())
        self.assertEqual(self.sync()[0], 0)

    def test_sync_refuses_bad_or_changed_source_and_tampered_destination(self):
        self.revision = self.revision[:8]
        self.assertEqual(self.sync()[0], 2)
        self.revision = self.git("rev-parse", "HEAD").strip()
        source_skill = self.source / "skills/coding-simplicity/SKILL.md"
        source_skill.write_text("changed\n")
        self.assertEqual(self.sync()[0], 2)
        source_skill.write_text(
            "---\nname: coding-simplicity\ndescription: fixture\n---\n\n# Fixture\n",
            encoding="utf-8",
        )
        self.assertEqual(self.sync()[0], 0)
        target = self.destination / "skills/coding-simplicity/SKILL.md"
        target.write_text("local change\n")
        self.assertEqual(self.sync()[0], 2)
        self.assertEqual(target.read_text(), "local change\n")

    def test_sync_refuses_nested_or_parent_destination_without_mutation(self):
        nested = self.source / "nested-consumer"
        nested.mkdir()
        original_destination = self.destination
        before = {p.relative_to(self.source): p.read_bytes()
                  for p in self.source.rglob("*") if p.is_file()}
        try:
            for destination in (nested, self.root):
                with self.subTest(destination=destination):
                    self.destination = destination
                    status, report = self.sync()
                    self.assertEqual(status, 2, report)
                    self.assertFalse(report["ok"])
                    self.assertIn("non-overlapping", report["error"])
                    self.assertFalse((destination / "skills").exists())
                    self.assertEqual(before, {p.relative_to(self.source): p.read_bytes()
                                              for p in self.source.rglob("*") if p.is_file()})
        finally:
            self.destination = original_destination

    def test_sync_refuses_a_supplied_symlink_root(self):
        linked = self.root / "linked-source"
        linked.symlink_to(self.source, target_is_directory=True)
        original = self.source
        self.source = linked
        self.assertEqual(self.sync()[0], 2)
        self.source = original

    def test_sync_refuses_a_symlinked_source_ancestor(self):
        linked_parent = self.root / "linked-parent"
        linked_parent.symlink_to(self.root, target_is_directory=True)
        original = self.source
        self.source = linked_parent / "agent-skills"
        self.assertEqual(self.sync()[0], 2)
        self.source = original

    def test_sync_refuses_a_noncanonical_source_origin(self):
        self.git("remote", "set-url", "origin", "https://github.com/example/other-skills.git")
        self.assertEqual(self.sync()[0], 2)

    def test_sync_refuses_a_symlinked_destination_component(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.destination / "skills").symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.sync()[0], 2)
        self.assertEqual(list(outside.iterdir()), [])

    def test_sync_replaces_only_an_unchanged_verified_snapshot(self):
        self.assertEqual(self.sync()[0], 0)
        changed = self.source / "skills/testing-best-practices/rules/example.md"
        changed.write_text("revised fixture\n")
        self.git("add", str(changed.relative_to(self.source)))
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "revised fixture")
        self.revision = self.git("rev-parse", "HEAD").strip()
        self.assertEqual(self.sync()[0], 2)
        status, report = self.sync("--replace", "--dry-run")
        self.assertEqual(status, 0, report)
        self.assertTrue(report["replaced"])
        self.assertEqual(self.sync("--replace")[0], 0)
        self.assertEqual(changed.read_bytes(), (self.destination / changed.relative_to(self.source)).read_bytes())
        manifest = json.loads((self.destination / "skills/portable-skills.json").read_text())
        self.assertEqual(manifest["source"]["revision"], self.revision)

    def test_sync_replace_refuses_a_changed_current_snapshot(self):
        self.assertEqual(self.sync()[0], 0)
        changed = self.source / "skills/testing-best-practices/rules/example.md"
        changed.write_text("revised fixture\n")
        self.git("add", str(changed.relative_to(self.source)))
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "revised fixture")
        self.revision = self.git("rev-parse", "HEAD").strip()
        current = self.destination / "skills/testing-best-practices/rules/example.md"
        current.write_text("local change\n")
        self.assertEqual(self.sync("--replace")[0], 2)
        self.assertEqual(current.read_text(), "local change\n")

    def test_replace_refuses_malformed_metadata_without_traceback_or_writes(self):
        self.assertEqual(self.sync()[0], 0)
        manifest_path = self.destination / "skills/portable-skills.json"
        original = manifest_path.read_text()
        for field in ("revision", "digest"):
            for value in (None, 17, [], {}):
                with self.subTest(field=field, value=value):
                    manifest = json.loads(original)
                    if field == "revision":
                        manifest["source"]["revision"] = value
                    else:
                        manifest["skills"]["coding-simplicity"]["files"]["SKILL.md"] = value
                    manifest_path.write_text(json.dumps(manifest))
                    before = {p.relative_to(self.destination): p.read_bytes()
                              for p in self.destination.rglob("*") if p.is_file()}
                    status, report = self.sync("--replace")
                    self.assertEqual(status, 2, report)
                    self.assertFalse(report["ok"])
                    self.assertEqual(before, {p.relative_to(self.destination): p.read_bytes()
                                             for p in self.destination.rglob("*") if p.is_file()})


if __name__ == "__main__":
    unittest.main()
