"""Standalone, side-effect-free bootstrap planning and OS capability tests."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.bootstrap_plan import PHP, main, package_manager, plan


class BootstrapPlanTest(unittest.TestCase):
    def test_debian_suggests_only_missing_fixed_packages(self) -> None:
        found = {"python3": "/usr/bin/python3", "git": "/usr/bin/git", "apt-get": "/usr/bin/apt-get"}
        result = plan("minimal", system="Linux", os_release={"ID": "debian"}, found=found)
        self.assertEqual(result["manager"], "apt")
        self.assertEqual(result["package_command_argv"], [
            "apt-get", "install", "--", "ripgrep", "jq", "curl",
            "fd-find", "shellcheck", "hyperfine", "strace",
        ])
        self.assertTrue(result["package_command_requires_privileges"])
        self.assertFalse(next(x for x in result["tools"] if x["name"] == "rg")["available"])

    def test_no_command_when_everything_is_present(self) -> None:
        found = {
            "apt-get": "/usr/bin/apt-get", "python3": "/python3", "git": "/git",
            "rg": "/rg", "jq": "/jq", "curl": "/curl", "fdfind": "/fdfind",
            "shellcheck": "/shellcheck", "hyperfine": "/hyperfine", "strace": "/strace",
        }
        result = plan("minimal", system="Linux", os_release={"ID": "ubuntu"}, found=found)
        self.assertIsNone(result["package_command_argv"])
        self.assertEqual(result["unmanaged_missing"], [])

    def test_diagnostics_are_default_and_debug_is_a_compatibility_alias(self) -> None:
        found = {"apt-get": "/usr/bin/apt-get"}
        default = plan("minimal", system="Linux", os_release={"ID": "debian"}, found=found)
        debug = plan("debug", system="Linux", os_release={"ID": "debian"}, found=found)
        php = plan("php", system="Linux", os_release={"ID": "debian"}, found=found)
        self.assertEqual(default["tools"], debug["tools"])
        self.assertEqual(default["package_command_argv"], debug["package_command_argv"])
        self.assertEqual([item["name"] for item in php["tools"]],
                         [item["name"] for item in default["tools"]] + ["php", "composer"])
        self.assertEqual(set(php["unmanaged_missing"]), {"php", "composer"})

    def test_diagnostics_remain_optional_and_never_execute(self) -> None:
        # The planner inspects paths only: missing debug binaries are recommendations.
        found = {"apt-get": "/usr/bin/apt-get", "python3": "/python3", "git": "/git"}
        report = plan("minimal", system="Linux", os_release={"ID": "debian"}, found=found)
        self.assertTrue(all(item["version"] is None for item in report["tools"]))
        self.assertTrue(report["package_command_requires_approval"])
        self.assertIn("strace", report["package_command_argv"])

    def test_debug_includes_strace_only_on_supported_linux(self) -> None:
        found = {"apt-get": "/usr/bin/apt-get"}
        linux = plan("debug", system="Linux", os_release={"ID": "ubuntu"}, found=found)
        self.assertIn("strace", linux["package_command_argv"])
        self.assertIn("strace", plan("minimal", system="Linux", os_release={"ID": "ubuntu"}, found=found)["package_command_argv"])
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

    def test_php_planner_and_diagnostic_names_agree(self) -> None:
        profile_path = Path(__file__).resolve().parents[1] / "profiles" / "php.json"
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        planner_names = {tool.name for tool in PHP}
        diagnostic_names = set(profile["required_tools"]) | set(profile["optional_tools"])
        self.assertEqual(planner_names, {"php", "composer"})
        self.assertTrue(planner_names.issubset(diagnostic_names))
        self.assertIn("php", profile["required_tools"])
        self.assertIn("composer", profile["optional_tools"])

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

    def test_entrypoint_only_discovers_matching_tools_on_path(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "firstInstall.sh"
        tool_names = (
            "apt-get", "brew", "composer", "curl", "fd", "fdfind", "git", "hyperfine",
            "jq", "php", "rg", "shellcheck", "strace",
        )
        with tempfile.TemporaryDirectory() as dirname:
            temporary = Path(dirname)
            tools = temporary / "tools"
            tools.mkdir()
            marker = temporary / "executed"
            for name in tool_names:
                fake = tools / name
                fake.write_text("#!/bin/sh\n: > \"$MARKER\"\nexit 99\n", encoding="utf-8")
                fake.chmod(0o755)
            (tools / "python3").symlink_to(sys.executable)
            res = subprocess.run(
                ["/bin/sh", str(script), "plan", "--profile", "debug"],
                cwd=temporary,
                env={"PATH": str(tools), "MARKER": str(marker)},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertFalse(marker.exists(), "the planner must not execute discovered tools")
            report = json.loads(res.stdout)
            self.assertTrue(all(item["available"] for item in report["tools"]))
            self.assertIsNone(report["package_command_argv"])

    def test_missing_python_has_actionable_error_without_mutation(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "firstInstall.sh"
        with tempfile.TemporaryDirectory() as dirname:
            res = subprocess.run(["/bin/sh", str(script), "plan"], cwd=dirname,
                                 env={"PATH": dirname}, capture_output=True,
                                 text=True, check=False)
            self.assertEqual(res.returncode, 2)
            self.assertIn("Python 3.10+ is required", res.stderr)
            self.assertFalse(tuple(Path(dirname).iterdir()))

    def test_unusable_python_has_actionable_error_without_mutation(self) -> None:
        root = Path(__file__).resolve().parents[1]
        script = root / "firstInstall.sh"
        with tempfile.TemporaryDirectory() as dirname:
            fake_python = Path(dirname) / "python3"
            fake_python.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
            fake_python.chmod(0o755)
            res = subprocess.run(["/bin/sh", str(script), "plan"], cwd=dirname,
                                 env={"PATH": dirname}, capture_output=True,
                                 text=True, check=False)
            self.assertEqual(res.returncode, 2)
            self.assertIn("Python 3.10+ is required", res.stderr)
            self.assertNotIn("Traceback", res.stderr)
            self.assertEqual([p.name for p in Path(dirname).iterdir()], ["python3"])

    def test_main_does_not_invoke_subprocesses(self) -> None:
        with patch("tools.bootstrap_plan.platform.system", return_value="Linux"), \
             patch("tools.bootstrap_plan.platform.freedesktop_os_release", return_value={"ID": "debian"}), \
             patch("tools.bootstrap_plan.shutil.which", return_value=None), \
             patch("tools.bootstrap_plan.print") as output:
            self.assertEqual(main(["plan", "--profile", "minimal"]), 0)
            self.assertEqual(json.loads(output.call_args.args[0])["manager"], None)


if __name__ == "__main__":
    unittest.main()
