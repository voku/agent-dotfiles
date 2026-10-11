"""Standalone, side-effect-free bootstrap planning and OS capability tests."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools.bootstrap_plan import main, package_manager, plan


class BootstrapPlanTest(unittest.TestCase):
    def test_debian_suggests_only_missing_fixed_packages(self) -> None:
        found = {"python3": "/usr/bin/python3", "git": "/usr/bin/git", "apt-get": "/usr/bin/apt-get"}
        result = plan("minimal", system="Linux", os_release={"ID": "debian"}, found=found)
        self.assertEqual(result["manager"], "apt")
        self.assertEqual(result["package_command_argv"], ["apt-get", "install", "--", "ripgrep", "jq", "curl"])
        self.assertTrue(result["package_command_requires_privileges"])
        self.assertFalse(next(x for x in result["tools"] if x["name"] == "rg")["available"])

    def test_no_command_when_everything_is_present(self) -> None:
        found = {"apt-get": "/usr/bin/apt-get", "python3": "/python3", "git": "/git", "rg": "/rg", "jq": "/jq", "curl": "/curl"}
        result = plan("minimal", system="Linux", os_release={"ID": "ubuntu"}, found=found)
        self.assertIsNone(result["package_command_argv"])
        self.assertEqual(result["unmanaged_missing"], [])

    def test_debug_includes_strace_only_on_supported_linux(self) -> None:
        found = {"apt-get": "/usr/bin/apt-get"}
        linux = plan("debug", system="Linux", os_release={"ID": "ubuntu"}, found=found)
        self.assertIn("strace", linux["package_command_argv"])
        mac = plan("debug", system="Darwin", os_release={}, found={"brew": "/opt/homebrew/bin/brew"})
        self.assertIn("strace", mac["unmanaged_missing"])
        self.assertNotIn("strace", mac["package_command_argv"])

    def test_unverified_os_yields_no_package_command(self) -> None:
        result = plan("minimal", system="Linux", os_release={"ID": "fedora"}, found={"apt-get": "/usr/bin/apt-get"})
        self.assertIsNone(result["manager"])
        self.assertIsNone(result["package_command_argv"])
        self.assertIn("rg", result["unmanaged_missing"])
        self.assertIsNone(package_manager("Darwin", {}, False, True))

    def test_php_does_not_assume_system_package_is_suitable(self) -> None:
        result = plan("php", system="Linux", os_release={"ID": "ubuntu"}, found={"apt-get": "/usr/bin/apt-get"})
        self.assertEqual(set(result["unmanaged_missing"]), {"php", "composer"})

    def test_fdfind_is_recognized(self) -> None:
        result = plan("debug", system="Linux", os_release={"ID": "debian"}, found={"apt-get": "/usr/bin/apt-get", "fdfind": "/usr/bin/fdfind"})
        item = next(x for x in result["tools"] if x["name"] == "fd")
        self.assertTrue(item["available"])
        self.assertEqual(item["command"], "fdfind")
        self.assertNotIn("fd-find", result["package_command_argv"])

    def test_real_readonly_entrypoint_outputs_json_and_writes_nothing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "firstInstall.sh"
        with tempfile.TemporaryDirectory() as dirname:
            before = tuple(Path(dirname).iterdir())
            res = subprocess.run([str(script), "plan"], cwd=dirname, capture_output=True, text=True, check=False)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertEqual(json.loads(res.stdout)["operation"], "plan")
            self.assertEqual(tuple(Path(dirname).iterdir()), before)

    def test_main_does_not_invoke_subprocesses(self) -> None:
        with patch("tools.bootstrap_plan.platform.system", return_value="Linux"), \
             patch("tools.bootstrap_plan.platform.freedesktop_os_release", return_value={"ID": "debian"}), \
             patch("tools.bootstrap_plan.shutil.which", return_value=None), \
             patch("tools.bootstrap_plan.print") as output:
            self.assertEqual(main(["plan", "--profile", "minimal"]), 0)
            self.assertEqual(json.loads(output.call_args.args[0])["manager"], None)


if __name__ == "__main__":
    unittest.main()
