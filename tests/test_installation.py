"""Pinned, isolated installation and fail-closed rollback contracts."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]
INSTALLER = PROJECT / "tools/install.py"


class InstallationTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        # macOS /var is a symlink to /private/var. Use the canonical private
        # fixture parent; production intentionally rejects symlink ancestors.
        self.root = Path(temporary.name).resolve()
        self.source = self.root / "source"
        self.source.mkdir()
        for name in ("agent_dotfiles", "bin", "shell", "skills", "profiles"):
            shutil.copytree(PROJECT / name, self.source / name,
                            ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copyfile(PROJECT / "LICENSE", self.source / "LICENSE")
        for name in (".bashrc", ".zshrc", ".shellrc", ".functions", ".exports"):
            (self.source / name).write_text(f"# independently known fixture: {name}\n")
        self.git("init", "-q")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "fixture")
        self.revision = self.git("rev-parse", "HEAD").strip()
        self.prefix = self.root / "isolated prefix"

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.source), *args], text=True)

    def command(self, command, *args):
        result = subprocess.run([sys.executable, str(INSTALLER), command,
                                 "--prefix", str(self.prefix), *args],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.stderr, "", result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["schema"], "agent-dotfiles.v1.installation")
        return result.returncode, report

    def install(self, revision=None):
        return self.command("install", "--source", str(self.source),
                            "--revision", revision or self.revision)

    def remove_skills_from_legacy_manifest(self, data):
        skill_paths = sorted(name for name in data["files"] if name.startswith("skills/"))
        for name in skill_paths:
            (self.prefix / name).unlink()
            del data["files"][name]
        directories = sorted({(self.prefix / Path(name).parent) for name in skill_paths},
                             key=lambda path: len(path.parts), reverse=True)
        for directory in directories:
            if directory.exists():
                directory.rmdir()

    def test_plan_is_read_only_and_matches_exact_install_manifest(self):
        status, report = self.command("plan", "--source", str(self.source),
                                      "--revision", self.revision)
        self.assertEqual(status, 0, report)
        self.assertTrue(report["ok"])
        self.assertEqual(report["operation"], "plan")
        self.assertEqual(report["source_revision"], self.revision)
        self.assertEqual(report["files"], len(report["entries"]))
        self.assertNotIn("installation.json", report["entries"])
        for name in ("bin/agent-dotfiles", ".bashrc", ".zshrc", ".shellrc",
                     "shell/modules/context.sh", "shell/modules/git.sh",
                     "shell/core/activation.sh", "shell/core/deactivation.sh",
                     "profiles/minimal.json", "profiles/git.json", "profiles/php.json", "profiles/shell.json",
                     "skills/project-onboarding/SKILL.md", "skills/portable-skills.json",
                     "skills/coding-simplicity/SKILL.md",
                     "skills/testing-best-practices/rules/cov-regression-first.md",
                     "skills/php-static-analysis/rules/sa-contract-honesty.md",
                     "skills/language-onboarding-authoring/SKILL.md"):
            self.assertIn(name, report["entries"])
        self.assertEqual(report["entries"]["bin/agent-dotfiles"]["mode"], 0o755)
        self.assertFalse(self.prefix.exists())
        self.assertEqual(list(self.root.glob(".agent-dotfiles-install-*")), [])
        self.assertEqual(self.install()[0], 0)
        manifest = json.loads((self.prefix / "installation.json").read_text())
        self.assertEqual(report["entries"], manifest["files"])
        self.assertEqual(self.command("uninstall")[0], 0)

    def test_existing_project_learning_is_never_shipped_as_environment(self):
        # The source repository may run agent-loop itself. Do not forbid that:
        # assert the immutable installed payload is independent of these files.
        project_only = {
            ".agent-loop/init.json": '{"version": 1}\n',
            ".agent-loop/learning/config.json": '{"schema_version": "1.0"}\n',
            ".agent-loop/learning/findings/validated/fixture.json": '{"id": "fixture"}\n',
            "MEMORY.md": "# Project-maintainer knowledge\n",
            "docs/recall-documents.json": '{"schema_version": "1.0", "documents": []}\n',
        }
        for relative, content in project_only.items():
            file = self.source / relative
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(content, encoding="utf-8")
        self.git("add", "--", *project_only)
        self.git(
            "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
            "commit", "-qm", "Source checkout legitimately runs agent-loop",
        )
        revision = self.git("rev-parse", "HEAD").strip()
        status, plan = self.command(
            "plan", "--source", str(self.source), "--revision", revision
        )
        self.assertEqual(status, 0, plan)
        self.assertTrue(plan["ok"])
        for relative in project_only:
            with self.subTest(path=relative):
                self.assertTrue((self.source / relative).is_file())
                self.assertNotIn(relative, plan["entries"])
        self.assertEqual(self.install(revision)[0], 0)
        manifest = json.loads((self.prefix / "installation.json").read_text())
        self.assertEqual(set(plan["entries"]), set(manifest["files"]))
        for relative in project_only:
            with self.subTest(path=relative):
                self.assertNotIn(relative, manifest["files"])
                self.assertFalse((self.prefix / relative).exists())
        self.assertEqual(self.command("verify")[0], 0)
        self.assertEqual(self.command("uninstall")[0], 0)

    def test_plan_refuses_bad_pin_dirty_checkout_and_occupied_prefix(self):
        self.assertEqual(self.command("plan", "--source", str(self.source),
                                      "--revision", self.revision[:8])[0], 2)
        changed = self.source / "agent_dotfiles/__init__.py"
        changed.write_text(changed.read_text() + "# dirty\n")
        self.assertEqual(self.command("plan", "--source", str(self.source),
                                      "--revision", self.revision)[0], 2)
        self.assertFalse(self.prefix.exists())
        changed.write_text(changed.read_text().removesuffix("# dirty\n"))
        self.prefix.mkdir()
        (self.prefix / "unrelated").write_text("keep")
        self.assertEqual(self.command("plan", "--source", str(self.source),
                                      "--revision", self.revision)[0], 2)
        self.assertEqual((self.prefix / "unrelated").read_text(), "keep")

    def test_install_doctor_verify_and_uninstall(self):
        self.assertEqual(self.install()[0], 0)
        result = subprocess.run([str(self.prefix / "bin/agent-dotfiles"), "doctor"],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["schema"], "agent-dotfiles.v1.doctor")
        self.assertFalse(list(self.prefix.rglob("__pycache__")))
        self.assertEqual(self.command("verify")[0], 0)
        self.assertEqual(self.command("uninstall")[0], 0)
        self.assertFalse(self.prefix.exists())

    def test_revision_must_be_full_and_match_head(self):
        for revision in (self.revision[:8], "0" * 40, "main"):
            with self.subTest(revision=revision):
                self.assertEqual(self.install(revision)[0], 2)
                self.assertFalse(self.prefix.exists())

    def test_checkout_root_preserves_trailing_whitespace(self):
        for suffix in (" ", "\n"):
            with self.subTest(suffix=suffix):
                original = self.source
                self.source = original.with_name("source" + suffix)
                original.rename(self.source)
                self.assertEqual(self.install()[0], 0)
                self.assertEqual(self.command("uninstall")[0], 0)
                self.source.rename(original)
                self.source = original

    def test_tracked_dirty_runtime_refused_staged_or_unstaged(self):
        target = self.source / "agent_dotfiles/__init__.py"
        target.write_text(target.read_text() + "\n# dirty\n")
        self.assertEqual(self.install()[0], 2)
        self.git("add", ".")
        self.assertEqual(self.install()[0], 2)
        self.assertFalse(self.prefix.exists())

    def test_untracked_runtime_injection_excluded(self):
        (self.source / "agent_dotfiles/injected.py").write_text("raise RuntimeError()")
        self.assertEqual(self.install()[0], 0)
        self.assertFalse((self.prefix / "agent_dotfiles/injected.py").exists())

    def test_modified_runtime_preserved(self):
        self.assertEqual(self.install()[0], 0)
        target = self.prefix / "agent_dotfiles/__init__.py"
        target.write_text("# local modification\n")
        self.assertEqual(self.command("verify")[0], 2)
        self.assertEqual(self.command("uninstall")[0], 2)
        self.assertEqual(target.read_text(), "# local modification\n")

    def test_unknown_file_and_empty_directory_preserved(self):
        self.assertEqual(self.install()[0], 0)
        unknown = self.prefix / "notes"
        unknown.write_text("keep me")
        self.assertEqual(self.command("uninstall")[0], 2)
        self.assertEqual(unknown.read_text(), "keep me")
        unknown.unlink()
        unknown.mkdir()
        self.assertEqual(self.command("uninstall")[0], 2)
        self.assertTrue(unknown.is_dir())

    def test_existing_nonempty_prefix_refused(self):
        self.prefix.mkdir()
        (self.prefix / "keep").write_text("keep")
        self.assertEqual(self.install()[0], 2)
        self.assertEqual((self.prefix / "keep").read_text(), "keep")

    def test_symlink_prefix_and_symlink_ancestor_refused(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.prefix.symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.install()[0], 2)
        self.prefix = self.prefix / "nested"
        self.assertEqual(self.install()[0], 2)
        self.assertEqual(list(outside.iterdir()), [])

    def test_source_symlink_refused(self):
        target = self.source / "agent_dotfiles/__init__.py"
        target.unlink()
        target.symlink_to(PROJECT / "agent_dotfiles/__init__.py")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "symlink")
        self.revision = self.git("rev-parse", "HEAD").strip()
        self.assertEqual(self.install()[0], 2)

    def test_installed_symlink_and_manifest_traversal_refused(self):
        self.assertEqual(self.install()[0], 0)
        manifest = self.prefix / "installation.json"
        data = json.loads(manifest.read_text())
        data["files"]["../outside"] = data["files"]["LICENSE"]
        manifest.write_text(json.dumps(data))
        self.assertEqual(self.command("uninstall")[0], 2)
        self.assertTrue((self.prefix / "LICENSE").exists())
        del data["files"]["../outside"]
        manifest.write_text(json.dumps(data))
        target = self.prefix / "LICENSE"
        target.unlink()
        target.symlink_to(PROJECT / "LICENSE")
        self.assertEqual(self.command("uninstall")[0], 2)
        self.assertTrue(target.is_symlink())

    def test_expected_pin_and_invalid_manifest_fail_closed(self):
        self.assertEqual(self.install()[0], 0)
        self.assertEqual(self.command("verify", "--revision", self.revision)[0], 0)
        self.assertEqual(self.command("uninstall", "--revision", "0" * 40)[0], 2)
        self.assertTrue(self.prefix.exists())
        manifest = self.prefix / "installation.json"
        for content in ("not json", "[]", '{"schema": "unknown"}'):
            with self.subTest(content=content):
                manifest.write_text(content)
                self.assertEqual(self.command("verify")[0], 2)
                self.assertEqual(self.command("uninstall")[0], 2)
                self.assertTrue((self.prefix / "LICENSE").exists())

    def test_permissions_changed_refuses_uninstall(self):
        self.assertEqual(self.install()[0], 0)
        executable = self.prefix / "bin/agent-dotfiles"
        executable.chmod(0o644)
        self.assertEqual(self.command("verify")[0], 2)
        self.assertEqual(self.command("uninstall")[0], 2)
        self.assertTrue(executable.exists())

    def test_profiles_are_pinned_copied_hashed_not_executed(self):
        profile = self.source / ".shellrc"
        marker = self.root / "must-not-exist"
        profile.write_text(f"touch '{marker}'\n")
        self.git("add", ".shellrc")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "profile fixture")
        self.revision = self.git("rev-parse", "HEAD").strip()
        self.assertEqual(self.install()[0], 0)
        for name in (".bashrc", ".zshrc", ".shellrc", ".functions", ".exports",
                     "shell/modules/context.sh", "shell/modules/git.sh",
                     "shell/core/activation.sh", "shell/core/deactivation.sh",
                     "skills/project-onboarding/SKILL.md"):
            self.assertEqual((self.prefix / name).read_bytes(), (self.source / name).read_bytes())
        self.assertFalse(marker.exists())
        self.assertEqual(self.command("verify")[0], 0)
        (self.prefix / ".exports").write_text("# consumer changes\n")
        self.assertEqual(self.command("verify")[0], 2)
        self.assertEqual(self.command("uninstall")[0], 2)
        self.assertEqual((self.prefix / ".exports").read_text(), "# consumer changes\n")

    def test_all_profiles_required_for_new_installations(self):
        self.git("rm", ".zshrc")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "missing profile")
        self.revision = self.git("rev-parse", "HEAD").strip()
        self.assertEqual(self.install()[0], 2)
        self.assertFalse(self.prefix.exists())

    def test_all_capability_profiles_required_for_new_installations(self):
        self.git("rm", "profiles/php.json")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "missing capability profile")
        self.revision = self.git("rev-parse", "HEAD").strip()
        self.assertEqual(self.install()[0], 2)
        self.assertFalse(self.prefix.exists())

    def test_all_modules_required_for_new_installations(self):
        self.git("rm", "shell/modules/git.sh")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "missing shell module")
        self.revision = self.git("rev-parse", "HEAD").strip()
        self.assertEqual(self.install()[0], 2)
        self.assertFalse(self.prefix.exists())

    def test_all_core_files_required_for_new_installations(self):
        self.git("rm", "shell/core/deactivation.sh")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "missing shell core")
        self.revision = self.git("rev-parse", "HEAD").strip()
        self.assertEqual(self.install()[0], 2)
        self.assertFalse(self.prefix.exists())

    def test_project_onboarding_skill_required_for_new_installations(self):
        self.git("rm", "skills/project-onboarding/SKILL.md")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "missing project onboarding skill")
        self.revision = self.git("rev-parse", "HEAD").strip()
        self.assertEqual(self.install()[0], 2)
        self.assertFalse(self.prefix.exists())

    def test_portable_skill_manifest_is_required_for_new_installations(self):
        self.git("rm", "skills/portable-skills.json")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "missing portable skill manifest")
        self.revision = self.git("rev-parse", "HEAD").strip()
        self.assertEqual(self.install()[0], 2)
        self.assertFalse(self.prefix.exists())

    def test_portable_installation_requires_project_onboarding_skill(self):
        self.assertEqual(self.install()[0], 0)
        manifest = self.prefix / "installation.json"
        data = json.loads(manifest.read_text())
        skill = "skills/project-onboarding/SKILL.md"
        (self.prefix / skill).unlink()
        del data["files"][skill]
        manifest.write_text(json.dumps(data))
        self.assertEqual(self.command("verify")[0], 2)
        self.assertEqual(self.command("uninstall")[0], 2)

    def test_modified_core_refuses_verify_and_uninstall(self):
        self.assertEqual(self.install()[0], 0)
        target = self.prefix / "shell/core/activation.sh"
        target.write_text("# modified\n")
        self.assertEqual(self.command("verify")[0], 2)
        self.assertEqual(self.command("uninstall")[0], 2)
        self.assertEqual(target.read_text(), "# modified\n")

    def test_modified_module_refuses_verify_and_uninstall(self):
        self.assertEqual(self.install()[0], 0)
        target = self.prefix / "shell/modules/git.sh"
        target.write_text("# modified\n")
        self.assertEqual(self.command("verify")[0], 2)
        self.assertEqual(self.command("uninstall")[0], 2)
        self.assertEqual(target.read_text(), "# modified\n")

    def test_partial_core_manifest_refused(self):
        self.assertEqual(self.install()[0], 0)
        manifest = self.prefix / "installation.json"
        data = json.loads(manifest.read_text())
        (self.prefix / "shell/core/deactivation.sh").unlink()
        del data["files"]["shell/core/deactivation.sh"]
        manifest.write_text(json.dumps(data))
        self.assertEqual(self.command("verify")[0], 2)
        self.assertEqual(self.command("uninstall")[0], 2)

    def test_partial_module_manifest_refused(self):
        self.assertEqual(self.install()[0], 0)
        manifest = self.prefix / "installation.json"
        data = json.loads(manifest.read_text())
        (self.prefix / "shell/modules/context.sh").unlink()
        del data["files"]["shell/modules/context.sh"]
        manifest.write_text(json.dumps(data))
        self.assertEqual(self.command("verify")[0], 2)
        self.assertEqual(self.command("uninstall")[0], 2)

    def test_skill_is_pinned_and_modified_skill_refuses_verify_and_uninstall(self):
        self.assertEqual(self.install()[0], 0)
        skill = "skills/project-onboarding/SKILL.md"
        self.assertEqual((self.prefix / skill).read_bytes(),
                         (self.source / skill).read_bytes())
        manifest = json.loads((self.prefix / "installation.json").read_text())
        self.assertIn(skill, manifest["files"])
        (self.prefix / skill).write_text("# changed skill\n")
        self.assertEqual(self.command("verify")[0], 2)
        self.assertEqual(self.command("uninstall")[0], 2)
        self.assertEqual((self.prefix / skill).read_text(), "# changed skill\n")

    def test_pre_core_modular_manifest_still_verifies_and_uninstalls(self):
        # Older v1 profiles had modules but no shell/core lifecycle files.
        self.assertEqual(self.install()[0], 0)
        manifest = self.prefix / "installation.json"
        data = json.loads(manifest.read_text())
        for name in ("shell/core/activation.sh", "shell/core/deactivation.sh"):
            (self.prefix / name).unlink()
            del data["files"][name]
        (self.prefix / "shell/core").rmdir()
        self.remove_skills_from_legacy_manifest(data)
        manifest.write_text(json.dumps(data))
        self.assertEqual(self.command("verify", "--revision", self.revision)[0], 0)
        self.assertEqual(self.command("uninstall", "--revision", self.revision)[0], 0)

    def test_pre_modular_shell_manifest_still_verifies_and_uninstalls(self):
        # Model v0.4.0: all five profiles exist, but no shell/modules/ tree.
        self.assertEqual(self.install()[0], 0)
        manifest = self.prefix / "installation.json"
        data = json.loads(manifest.read_text())
        for name in ("shell/modules/context.sh", "shell/modules/git.sh",
                     "shell/core/activation.sh", "shell/core/deactivation.sh"):
            (self.prefix / name).unlink()
            del data["files"][name]
        (self.prefix / "shell/modules").rmdir()
        (self.prefix / "shell/core").rmdir()
        (self.prefix / "shell").rmdir()
        self.remove_skills_from_legacy_manifest(data)
        manifest.write_text(json.dumps(data))
        self.assertEqual(self.command("verify", "--revision", self.revision)[0], 0)
        self.assertEqual(self.command("uninstall", "--revision", self.revision)[0], 0)
        self.assertFalse(self.prefix.exists())

    def test_cli_only_legacy_manifest_still_verifies_and_uninstalls(self):
        self.assertEqual(self.install()[0], 0)
        manifest = self.prefix / "installation.json"
        data = json.loads(manifest.read_text())
        for name in (".bashrc", ".zshrc", ".shellrc", ".functions", ".exports",
                     "shell/modules/context.sh", "shell/modules/git.sh",
                     "shell/core/activation.sh", "shell/core/deactivation.sh"):
            (self.prefix / name).unlink()
            del data["files"][name]
        (self.prefix / "shell/modules").rmdir()
        (self.prefix / "shell/core").rmdir()
        (self.prefix / "shell").rmdir()
        self.remove_skills_from_legacy_manifest(data)
        manifest.write_text(json.dumps(data))
        self.assertEqual(self.command("verify", "--revision", self.revision)[0], 0)
        self.assertEqual(self.command("uninstall", "--revision", self.revision)[0], 0)

    def test_partial_profile_manifest_refused(self):
        self.assertEqual(self.install()[0], 0)
        manifest = self.prefix / "installation.json"
        data = json.loads(manifest.read_text())
        (self.prefix / ".bashrc").unlink()
        del data["files"][".bashrc"]
        manifest.write_text(json.dumps(data))
        self.assertEqual(self.command("verify")[0], 2)
        self.assertEqual(self.command("uninstall")[0], 2)

    def frontend(self, *arguments):
        return subprocess.run([str(self.source / "install.sh"), *arguments],
                              capture_output=True, text=True, timeout=15)

    def frontend_fixture(self):
        shutil.copyfile(PROJECT / "install.sh", self.source / "install.sh")
        (self.source / "install.sh").chmod(0o755)
        (self.source / "tools").mkdir()
        shutil.copyfile(INSTALLER, self.source / "tools/install.py")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "frontend fixture")
        self.revision = self.git("rev-parse", "HEAD").strip()

    def test_frontend_plan_is_read_only_from_unusual_root(self):
        self.frontend_fixture()
        original = self.source
        self.source = original.with_name("source with space 雪\n")
        original.rename(self.source)
        args = ("--prefix", str(self.prefix), "--revision", self.revision)
        result = self.frontend("plan", *args)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        plan = json.loads(result.stdout)
        self.assertEqual(plan["operation"], "plan")
        self.assertEqual(plan["source_revision"], self.revision)
        self.assertIn("shell/modules/context.sh", plan["entries"])
        self.assertFalse(self.prefix.exists())

    def test_frontend_default_install_and_explicit_lifecycle_unusual_root(self):
        self.frontend_fixture()
        original = self.source
        self.source = original.with_name("source with space 雪\n")
        original.rename(self.source)
        arguments = ("--prefix", str(self.prefix), "--revision", self.revision)
        result = self.frontend(*arguments)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(json.loads(result.stdout)["operation"], "install")
        result = self.frontend("verify", *arguments)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        result = self.frontend("uninstall", *arguments)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertFalse(self.prefix.exists())

    def test_frontend_refuses_relative_prefix_and_requires_explicit_pin(self):
        self.frontend_fixture()
        result = self.frontend("--prefix", "relative-prefix", "--revision", self.revision)
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.source / "relative-prefix").exists())
        result = self.frontend("--prefix", str(self.prefix))
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.prefix.exists())

    def test_frontend_rejects_abbreviated_source_override(self):
        """A full valid alternate checkout must not bypass the root installer owner."""
        self.frontend_fixture()
        alternate = self.root / "other valid checkout"
        shutil.copytree(self.source, alternate)
        for source_option in ("--source", "--sour", "--sourc"):
            with self.subTest(option=source_option):
                result = self.frontend("--prefix", str(self.prefix), "--revision",
                                       self.revision, source_option, str(alternate))
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertFalse(self.prefix.exists())

    def test_frontend_missing_python_has_visible_error(self):
        self.frontend_fixture()
        empty_path = self.root / "no-executables"
        empty_path.mkdir()
        result = subprocess.run([str(self.source / "install.sh"), "verify", "--prefix", str(self.prefix)],
                                env={**os.environ, "PATH": str(empty_path)}, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("python3 is required", result.stderr)
        self.assertFalse(self.prefix.exists())


if __name__ == "__main__":
    unittest.main()
