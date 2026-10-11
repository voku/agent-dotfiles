"""Executable contracts. No network, interactive shell, or optional CLI dependency."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parent.parent
CLI = PROJECT / "bin" / "agent-dotfiles"


class AgentDotfilesCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)
        self.tools = self.root / "tools"
        self.tools.mkdir()
        self.project = self.root / "project"
        self.project.mkdir()

    def executable(self, name: str, body: str) -> None:
        script = self.tools / name
        script.write_text(f"#!{sys.executable}\n{body}\n", encoding="utf-8")
        script.chmod(0o755)

    def cli(self, *arguments: str) -> tuple[int, dict[str, object]]:
        env = os.environ.copy()
        env["PATH"] = str(self.tools)
        env["LC_ALL"] = "C"
        result = subprocess.run(
            [sys.executable, str(CLI), *arguments],
            cwd=self.project,
            env=env,
            text=True,
            capture_output=True,
            timeout=8,
            check=False,
        )
        self.assertEqual(result.stderr, "", result.stderr)
        return result.returncode, json.loads(result.stdout)

    def test_doctor_reports_missing_without_installing(self) -> None:
        code, report = self.cli("doctor")
        self.assertEqual(code, 0)
        self.assertEqual(report["schema"], "agent-dotfiles.v1.doctor")
        self.assertFalse(report["required"]["rg"]["available"])
        self.assertEqual(report["missing_required"], ["rg", "git"])
        self.assertFalse(report["shell_startup_loaded"])
        self.assertFalse(report["installation_performed"])
        self.assertEqual(list(self.tools.iterdir()), [])

    def test_doctor_strict_missing_required_exits_two(self) -> None:
        code, report = self.cli("doctor", "--strict")
        self.assertEqual(code, 2)
        self.assertEqual(report["missing_required"], ["rg", "git"])

    def test_doctor_never_assumes_sg_is_ast_grep(self) -> None:
        self.executable("sg", "raise SystemExit(0)")
        code, report = self.cli("doctor")
        self.assertEqual(code, 0)
        self.assertFalse(report["optional"]["ast-grep"]["available"])
        self.assertNotIn("sg", report["optional"])

    def test_doctor_detects_fdfind_without_fd(self) -> None:
        self.executable("fdfind", "pass")
        code, report = self.cli("doctor")
        self.assertEqual(code, 0)
        self.assertEqual(report["optional"]["fd"]["executable"], "fdfind")
        self.assertTrue(report["optional"]["fd"]["available"])

    def test_files_preserves_spaces_and_newlines(self) -> None:
        self.executable("rg", "import sys\nsys.stdout.buffer.write(b'normal path.php\\0name\\nwith newline.php\\0')")
        code, report = self.cli("files", "--root", str(self.project))
        self.assertEqual(code, 0)
        self.assertEqual(report["paths"], ["normal path.php", "name\nwith newline.php"])
        self.assertFalse(report["truncated"])

    def test_files_are_bounded_and_truncation_is_reported(self) -> None:
        self.executable("rg", "import sys\nsys.stdout.buffer.write(b'a\\0b\\0c\\0')")
        code, report = self.cli("files", "--limit", "1")
        self.assertEqual(code, 3)
        self.assertEqual(report["paths"], ["a"])
        self.assertTrue(report["truncated"])

    def test_files_missing_tool_is_explicit_error(self) -> None:
        code, report = self.cli("files")
        self.assertEqual(code, 2)
        self.assertEqual(report["error"], "tool_missing")

    def test_fd_engine_executes_binary_even_when_shell_fd_function_exists(self) -> None:
        self.executable("fd", "import sys\nassert sys.argv[1:5] == ['--type', 'f', '--print0', '--color']\nsys.stdout.buffer.write(b'./readme file.md\\0')")
        code, report = self.cli("files", "--engine", "fd")
        self.assertEqual(code, 0)
        self.assertEqual(report["paths"], ["./readme file.md"])

    def test_search_emits_only_match_data_and_preserves_provider_byte_fields(self) -> None:
        self.executable(
            "rg",
            "import sys,json\n"
            "assert '--fixed-strings' in sys.argv\n"
            "assert sys.argv[-3:] == ['--', '-pattern', '.']\n"
            "print(json.dumps({'type':'begin','data':{'path':{'text':'a.php'}}}))\n"
            "print(json.dumps({'type':'match','data':{'path':{'bytes':'YQ=='},'line_number':9,'lines':{'text':'hello'}}}))\n"
            "print(json.dumps({'type':'end','data':{}}))",
        )
        code, report = self.cli("search", "--", "-pattern")
        self.assertEqual(code, 0)
        self.assertEqual(report["matches"], [{"path": {"bytes": "YQ=="}, "line_number": 9, "lines": {"text": "hello"}}])
        self.assertFalse(report["truncated"])

    def test_search_no_match_has_distinct_exit_code(self) -> None:
        self.executable("rg", "raise SystemExit(1)")
        code, report = self.cli("search", "nothing")
        self.assertEqual(code, 1)
        self.assertEqual(report["matches"], [])
        self.assertFalse(report["truncated"])

    def test_search_truncates_match_count_not_nonmatch_events(self) -> None:
        self.executable(
            "rg",
            "import json\n"
            "print(json.dumps({'type':'begin','data':{}}))\n"
            "for index in (1, 2, 3):\n"
            "  print(json.dumps({'type':'match','data':{'line_number':index}}))",
        )
        code, report = self.cli("search", "test", "--limit", "2")
        self.assertEqual(code, 3)
        self.assertEqual([m["line_number"] for m in report["matches"]], [1, 2])
        self.assertTrue(report["truncated"])

    def test_git_status_parses_rename_and_newline_path(self) -> None:
        self.executable(
            "git",
            "import sys\n"
            "assert sys.argv[1:] == ['status', '--porcelain=v1', '-z', '--untracked-files=all']\n"
            "sys.stdout.buffer.write(b' M file with space.php\\0?? new\\nname.php\\0R  target.php\\0original.php\\0')",
        )
        code, report = self.cli("git-status")
        self.assertEqual(code, 0)
        self.assertEqual(report["changes"], [
            {"xy": " M", "path": "file with space.php"},
            {"xy": "??", "path": "new\nname.php"},
            {"xy": "R ", "path": "target.php", "original_path": "original.php"},
        ])

    def test_git_status_truncated_not_complete(self) -> None:
        self.executable("git", "import sys\nsys.stdout.buffer.write(b'?? a\\0?? b\\0')")
        code, report = self.cli("git-status", "--limit", "1")
        self.assertEqual(code, 3)
        self.assertEqual(report["changes"], [{"xy": "??", "path": "a"}])
        self.assertTrue(report["truncated"])

    def test_git_status_rejects_incomplete_rename(self) -> None:
        self.executable("git", "import sys\nsys.stdout.buffer.write(b'R  target.php\\0')")
        code, report = self.cli("git-status")
        self.assertEqual(code, 2)
        self.assertEqual(report["error"], "invalid_tool_output")

    def test_invalid_rg_json_fails_closed(self) -> None:
        self.executable("rg", "print('not JSON')")
        code, report = self.cli("search", "test")
        self.assertEqual(code, 2)
        self.assertEqual(report["error"], "invalid_tool_output")

    def test_read_preserves_complete_selected_lines_and_hash(self) -> None:
        import hashlib
        raw = b"first\r\nsecond \xe2\x80\xa8 unicode\nthird without newline"
        (self.project / "source.php").write_bytes(raw)
        code, report = self.cli("read", "source.php", "--start", "2", "--end", "3")
        self.assertEqual(code, 0)
        self.assertEqual(report["content"], "second \u2028 unicode\nthird without newline")
        self.assertEqual(report["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(report["total_lines"], 3)
        self.assertFalse(report["complete_file"])
        self.assertFalse(report["truncated"])

    def test_read_digest_identifies_source_across_ranges(self) -> None:
        import hashlib
        raw = b"first\r\nsecond \xe2\x80\xa8 unicode\nthird without newline"
        (self.project / "ranges.txt").write_bytes(raw)
        lines = ["first\r\n", "second \u2028 unicode\n", "third without newline"]
        for start, end in ((1, 1), (2, 2), (3, 10), (1, 10)):
            with self.subTest(start=start, end=end):
                code, report = self.cli("read", "ranges.txt", "--start", str(start), "--end", str(end))
                content = "".join(lines[start - 1:min(end, 3)])
                self.assertEqual(code, 0)
                self.assertEqual(report["sha256"], hashlib.sha256(raw).hexdigest())
                self.assertEqual(report["content"], content)
                self.assertEqual(report["content_bytes"], len(content.encode("utf-8")))
                self.assertEqual(report["start"], start)
                self.assertEqual(report["requested_end"], end)
                self.assertEqual(report["actual_end"], min(end, 3))
                self.assertEqual(report["total_lines"], 3)
                self.assertEqual(report["complete_file"], start == 1 and end >= 3)
                self.assertFalse(report["truncated"])

    def test_read_short_file_reports_eof_instead_of_hidden_truncation(self) -> None:
        (self.project / "one.php").write_text("hello\n", encoding="utf-8")
        code, report = self.cli("read", "one.php")
        self.assertEqual(code, 0)
        self.assertEqual(report["requested_end"], 80)
        self.assertEqual(report["actual_end"], 1)
        self.assertTrue(report["complete_file"])
        self.assertEqual(report["content"], "hello\n")

    def test_read_rejects_path_traversal_and_symlink_escape(self) -> None:
        outside = self.root / "secret.php"
        outside.write_text("PRIVATE", encoding="utf-8")
        (self.project / "escape.php").symlink_to(outside)
        for name in ("../secret.php", "escape.php", str(outside)):
            with self.subTest(path=name):
                code, report = self.cli("read", name)
                self.assertEqual(code, 2)
                self.assertEqual(report["error"], "path_escape")

    def test_read_fail_closed_on_invalid_bytes(self) -> None:
        (self.project / "binary.php").write_bytes(b"bad\xffbytes")
        code, report = self.cli("read", "binary.php")
        self.assertEqual(code, 2)
        self.assertEqual(report["error"], "invalid_encoding")

    def test_read_rejects_oversized_range_before_access(self) -> None:
        code, report = self.cli("read", "any.php", "--start", "1", "--end", "500")
        self.assertEqual(code, 2)
        # Missing file takes precedence; check the range on a real file.
        (self.project / "any.php").write_text("yes", encoding="utf-8")
        code, report = self.cli("read", "any.php", "--start", "1", "--end", "500")
        self.assertEqual(code, 2)
        self.assertEqual(report["error"], "invalid_range")

    def test_tracked_files_keep_nul_separated_names(self) -> None:
        self.executable("git", "import sys\nassert sys.argv[1:] == ['ls-files', '--cached', '--full-name', '-z']\nsys.stdout.buffer.write(b'a b.php\\0c\\nname.php\\0')")
        code, report = self.cli("tracked")
        self.assertEqual(code, 0)
        self.assertEqual(report["paths"], ["a b.php", "c\nname.php"])
        self.assertEqual(report["selection"], "git-index-only; ignores untracked and excluded files")

    def test_git_patch_preserves_complete_patch_and_hash(self) -> None:
        import hashlib
        (self.project / "file.php").write_text("example", encoding="utf-8")
        self.executable("git", "import sys\nassert 'HEAD~1' in sys.argv and sys.argv[-2:] == ['--', 'file.php']\nassert '--binary' in sys.argv and '--full-index' in sys.argv\nassert '--no-ext-diff' in sys.argv\nif '--name-only' in sys.argv:\n  sys.stdout.buffer.write(b'file.php\\0')\nelse:\n  sys.stdout.buffer.write(b'diff --git a/file.php b/file.php\\n+full line\\n')")
        code, report = self.cli("git-patch", "file.php", "--base", "HEAD~1")
        self.assertEqual(code, 0)
        patch = b"diff --git a/file.php b/file.php\n+full line\n"
        self.assertEqual(report["patch"], {"text": patch.decode()})
        self.assertEqual(report["sha256"], hashlib.sha256(patch).hexdigest())
        self.assertFalse(report["truncated"])

    def test_git_patch_rejects_path_escape(self) -> None:
        code, report = self.cli("git-patch", "../../private")
        self.assertEqual(code, 2)
        self.assertEqual(report["error"], "path_escape")

    def test_git_patch_on_tool_error_returns_no_partial_patch(self) -> None:
        self.executable("git", "import sys\nprint('partial!')\nprint('failure', file=sys.stderr)\nraise SystemExit(128)")
        code, report = self.cli("git-patch", "missing.php")
        self.assertEqual(code, 2)
        self.assertEqual(report["error"], "tool_failed")
        self.assertNotIn("patch", report)

    def test_search_never_uses_max_column_preview(self) -> None:
        self.executable("rg", "import sys,json\nassert not any(x.startswith('--max-columns') for x in sys.argv)\nprint(json.dumps({'type':'match','data':{'lines':{'text':'x'*4000},'line_number':4}}))")
        code, report = self.cli("search", "x")
        self.assertEqual(code, 0)
        self.assertEqual(len(report["matches"][0]["lines"]["text"]), 4000)

    def test_environment_suppresses_user_ripgrep_config(self) -> None:
        self.executable("rg", "import os,sys,json\nassert os.environ.get('RIPGREP_CONFIG_PATH') == os.devnull\nprint(json.dumps({'type':'match','data':{'line_number':1}}))")
        code, report = self.cli("search", "x")
        self.assertEqual(code, 0)
        self.assertEqual(report["matches"][0]["line_number"], 1)

    def test_git_integration_real_repo(self) -> None:
        git = shutil.which("git")
        if git is None:
            self.skipTest("git unavailable")
        (self.project / "a file.php").write_text("before\n", encoding="utf-8")
        subprocess.run([git, "init", "-q"], cwd=self.project, check=True)
        subprocess.run([git, "add", "a file.php"], cwd=self.project, check=True)
        subprocess.run([git, "-c", "user.name=Test", "-c", "user.email=test@example.test", "commit", "-q", "-m", "initial"], cwd=self.project, check=True)
        (self.project / "a file.php").write_text("after\n", encoding="utf-8")
        shutil.copy(git, self.tools / "git")
        code, status = self.cli("git-status")
        self.assertEqual(code, 0)
        self.assertEqual(status["changes"], [{"xy": " M", "path": "a file.php"}])
        code, report = self.cli("git-patch", "a file.php")
        self.assertEqual(code, 0)
        self.assertIn("-before", report["patch"]["text"])
        self.assertIn("+after", report["patch"]["text"])
        code, tracked = self.cli("tracked")
        self.assertEqual(code, 0)
        self.assertEqual(tracked["paths"], ["a file.php"])

    def test_search_explicit_scope_and_glob_no_truncation_flags(self) -> None:
        (self.project / "src").mkdir()
        self.executable("rg", "import sys,json\nassert sys.argv[-3:] == ['--', 'foo', 'src']\nassert '--glob=*.php' in sys.argv\nassert '--glob=!vendor/**' in sys.argv\nassert '--max-columns-preview' not in sys.argv\nprint(json.dumps({'type':'match','data':{'line_number':1}}))")
        code, report = self.cli("search", "foo", "--path", "src", "--glob", "*.php", "--glob", "!vendor/**")
        self.assertEqual(code, 0)
        self.assertEqual(report["selection"]["path"], "src")
        self.assertEqual(report["selection"]["globs"], ["*.php", "!vendor/**"])

    def test_search_scope_symlink_outside_root_denied(self) -> None:
        (self.project / "outside").symlink_to(self.root)
        code, report = self.cli("search", "foo", "--path", "outside")
        self.assertEqual(code, 2)
        self.assertEqual(report["error"], "path_escape")

    def test_git_index_output_is_bounded(self) -> None:
        self.executable("git", "import sys\nif sys.argv[1] == 'ls-files':\n  sys.stdout.buffer.write(b'a'*(3*1024*1024))")
        code, report = self.cli("git-patch", "missing.php")
        self.assertEqual(2, code)
        self.assertEqual("output_too_large", report["error"])
        self.assertNotIn("patch", report)

    def test_git_patch_cap_is_explicit_error_without_partial_patch(self) -> None:
        self.executable("git", "import sys\nsys.stdout.buffer.write(b'a'*(3*1024*1024))")
        code, report = self.cli("git-patch", "file.php")
        self.assertEqual(code, 2)
        self.assertEqual(report["error"], "output_too_large")
        self.assertNotIn("patch", report)

    def test_aliases_are_optional_and_read_only(self) -> None:
        config_path = PROJECT / "config" / "gitconfig.agent.example"
        config_text = config_path.read_text(encoding="utf-8")
        self.assertNotIn("!", config_text.split("[alias]", 1)[1])
        self.assertNotIn("push", config_text.split("[alias]", 1)[1])
        self.assertNotIn("reset", config_text.split("[alias]", 1)[1])
        git = shutil.which("git")
        if git is None:
            self.skipTest("git unavailable")
        result = subprocess.run(
            [git, "-c", f"include.path={config_path}", "config", "alias.agent-patch"],
            cwd=self.project, capture_output=True, text=True, check=True,
        )
        self.assertIn("--binary --full-index", result.stdout)

    def test_limit_validation_rejects_zero(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CLI), "files", "--limit", "0"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("between 1 and 1000", result.stderr)


if __name__ == "__main__":
    unittest.main()
