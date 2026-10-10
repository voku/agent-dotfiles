"""Fast, mutation-targeted tests for safety-critical input validation."""

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile
import unittest

from agent_dotfiles.validation import CommandFailure, MAX_LIMIT, _relative_path, _valid_limit


class ValidationMutationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = (Path(self.tmp.name) / "workspace").resolve()
        self.root.mkdir()
        (self.root / "src").mkdir()
        (self.root / "src" / "hello.php").write_text("hello\n")

    def assert_denied(self, path: str, reason: str) -> None:
        with self.assertRaises(CommandFailure) as error:
            _relative_path(self.root, path)
        self.assertEqual(error.exception.reason, reason)

    def test_regular_and_nested_paths(self) -> None:
        self.assertEqual(_relative_path(self.root, "src/hello.php"), "src/hello.php")
        self.assertEqual(_relative_path(self.root, "src/../src/hello.php"), "src/hello.php")

    def test_absolute_inside_root_is_normalized(self) -> None:
        self.assertEqual(_relative_path(self.root, str(self.root / "src" / "hello.php")), "src/hello.php")

    def test_unicode_and_spaces_preserved(self) -> None:
        name = "a b-ü.php"
        (self.root / name).write_text("content", encoding="utf-8")
        self.assertEqual(_relative_path(self.root, name), name)

    def test_empty_root_marker_denied(self) -> None:
        for p in ("", ".", "./", "src/.."):
            with self.subTest(path=p):
                self.assert_denied(p, "invalid_file")

    def test_parent_escape_denied(self) -> None:
        for p in ("../private.php", "src/../../outside.php"):
            with self.subTest(path=p):
                self.assert_denied(p, "path_escape")

    def test_absolute_outside_denied(self) -> None:
        other = Path(self.tmp.name) / "outside.php"
        other.write_text("nope")
        self.assert_denied(str(other), "path_escape")

    def test_symlink_outside_denied(self) -> None:
        outside = Path(self.tmp.name) / "private"
        outside.write_text("secret")
        (self.root / "escape").symlink_to(outside)
        self.assert_denied("escape", "path_escape")

    def test_symlink_inside_root_canonicalized(self) -> None:
        (self.root / "inside").symlink_to(self.root / "src")
        self.assertEqual(_relative_path(self.root, "inside/hello.php"), "src/hello.php")

    def test_limits_minimum_and_maximum(self) -> None:
        self.assertEqual(_valid_limit("1"), 1)
        self.assertEqual(_valid_limit(str(MAX_LIMIT)), MAX_LIMIT)
        self.assertEqual(_valid_limit("42"), 42)

    def test_limits_out_of_range(self) -> None:
        for p in ("0", "-1", str(MAX_LIMIT + 1), "999999"):
            with self.subTest(value=p), self.assertRaisesRegex(argparse.ArgumentTypeError, "between 1 and"):
                _valid_limit(p)

    def test_limits_not_numbers(self) -> None:
        for p in ("foo", "1.5", ""):
            with self.subTest(value=p), self.assertRaisesRegex(argparse.ArgumentTypeError, "must be an integer"):
                _valid_limit(p)


if __name__ == "__main__":
    unittest.main()
