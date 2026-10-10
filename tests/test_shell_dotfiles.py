"""Real installed Bash/Zsh helpers, optional activation and fallback contracts."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]


class ShellDotfilesTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name).resolve()
        self.source = root / "source"
        self.source.mkdir()
        self.prefix = root / "consumer"
        for name in ("agent_dotfiles", "bin", "shell", "tools"):
            shutil.copytree(PROJECT / name, self.source / name,
                            ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("LICENSE", "install.sh"):
            shutil.copyfile(PROJECT / name, self.source / name)
        self.git("init", "-q")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "fixture")
        self.revision = self.git("rev-parse", "HEAD").strip()
        result = subprocess.run(["bash", str(self.source / "install.sh"), "install",
                                 "--revision", self.revision, "--prefix", str(self.prefix)],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue(json.loads(result.stdout)["ok"])

    def git(self, *args: str) -> str:
        return subprocess.check_output(
            ["git", "-C", str(self.source), *args], text=True
        )

    def run_profile(self, executable: str, profile: str, script: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [executable, "-c", script, "agent-test", str(self.prefix / "shell" / profile)],
            cwd=self.source, text=True, capture_output=True, timeout=15,
        )

    def assert_profile(self, executable: str, profile: str) -> None:
        script = (
            'previous_path="$PATH"; '
            '. "$1" || exit $?; '
            '[ "$PATH" = "$previous_path" ] || exit 88; '
            'agent_doctor || exit $?; '
            'agent_history 1 || exit $?; '
            'agent_blame LICENSE 1 1 || exit $?'
        )
        result = self.run_profile(executable, profile, script)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout.splitlines()[0])["schema"], "agent-dotfiles.v1.doctor")
        self.assertIn("commit ", result.stdout)
        self.assertIn("author ", result.stdout)
        self.assertEqual(
            subprocess.run(["bash", str(self.source / "install.sh"), "verify",
                            "--revision", self.revision, "--prefix", str(self.prefix)],
                           capture_output=True, text=True, timeout=15).returncode, 0
        )

    def test_bash_installed_profile(self) -> None:
        self.assert_profile("bash", ".bashrc")

    @unittest.skipUnless(shutil.which("zsh"), "Zsh is not installed")
    def test_zsh_installed_profile(self) -> None:
        self.assert_profile("zsh", ".zshrc")

    def test_existing_function_is_not_overwritten(self) -> None:
        result = self.run_profile(
            "bash", ".bashrc",
            'agent_files() { printf preserved; }; '
            '. "$1"; status=$?; [ "$status" -eq 2 ] || exit 9; '
            '[ "$(agent_files)" = preserved ] || exit 10; '
            'type agent_doctor >/dev/null 2>&1 && exit 11; exit 0',
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_invalid_history_and_blame_rejected(self) -> None:
        result = self.run_profile(
            "bash", ".bashrc",
            '. "$1" || exit $?; '
            'agent_history --all >/dev/null 2>&1 && exit 11; '
            'agent_history 1001 >/dev/null 2>&1 && exit 12; '
            'agent_blame LICENSE 0 1 >/dev/null 2>&1 && exit 13; '
            'agent_blame LICENSE 2 1 >/dev/null 2>&1 && exit 14; exit 0',
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_modified_shell_asset_blocks_uninstall(self) -> None:
        profile = self.prefix / "shell/.bashrc"
        profile.write_text(profile.read_text() + "\n# modified\n")
        result = subprocess.run(
            ["bash", str(self.source / "install.sh"), "uninstall", "--revision",
             self.revision, "--prefix", str(self.prefix)],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 2)
        self.assertTrue(profile.exists())


if __name__ == "__main__":
    unittest.main()
