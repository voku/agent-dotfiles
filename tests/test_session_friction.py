import json
import tempfile
import unittest
from pathlib import Path

from tools import session_friction


class SessionFrictionTest(unittest.TestCase):
    def write_trace(self, directory: str, name: str, rows: list[dict]) -> Path:
        path = Path(directory) / name
        path.write_text(
            "".join(json.dumps(row) + "\n" for row in rows),
            encoding="utf-8",
        )
        return path

    def test_repeated_normalized_command_is_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_trace(
                tmp,
                "trace.jsonl",
                [{"kind": "command", "value": "git status", "success": True}] * 3,
            )
            report = session_friction.analyze([path], "normalized")

        self.assertEqual(3, report["events"]["recognized"])
        self.assertEqual("repeated_command", report["candidates"][0]["kind"])

    def test_repeated_failures_and_command_churn_are_candidates(self) -> None:
        rows = [
            {"kind": "command", "value": "php -v", "success": False},
            {"kind": "command", "value": "php --version", "success": False},
            {"kind": "command", "value": "php -v", "success": False},
        ]
        events = session_friction.normalize_records(rows, "normalized")
        candidates = session_friction.find_candidates(events)
        kinds = {candidate.kind for candidate in candidates}

        self.assertIn("repeated_failed_command", kinds)
        self.assertIn("command_failure_churn", kinds)

    def test_auto_extracts_codex_like_nested_command(self) -> None:
        rows = [
            {
                "type": "tool_call",
                "tool_name": "exec_command",
                "arguments": {"command": "rg -n Foo src"},
                "result": {"exit_code": 0},
            }
        ]
        events = session_friction.normalize_records(rows, "auto")

        self.assertEqual(1, len(events))
        self.assertEqual("command", events[0].kind)
        self.assertEqual("rg -n Foo src", events[0].signature)
        self.assertTrue(events[0].success)

    def test_auto_extracts_claude_like_bash_and_read(self) -> None:
        rows = [
            {
                "name": "Bash",
                "input": {"command": "./vendor/bin/phpunit --filter Foo"},
                "status": "failed",
            },
            {"name": "Read", "input": {"file_path": "src/Foo.php"}},
        ]
        events = session_friction.normalize_records(rows, "auto")

        self.assertEqual(["command", "read"], [event.kind for event in events])
        self.assertFalse(events[0].success)
        self.assertEqual("src/Foo.php", events[1].signature)

    def test_malformed_jsonl_reports_source_location(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.jsonl"
            path.write_text('{"kind":"command"}\n{nope}\n', encoding="utf-8")

            with self.assertRaisesRegex(session_friction.TraceError, r"broken\.jsonl:2:"):
                session_friction.load_records(path)

    def test_secret_like_values_are_redacted_in_candidate_samples(self) -> None:
        events = [
            session_friction.Event(
                index=index,
                kind="command",
                signature="curl --token abc123 https://example.test",
                success=True,
            )
            for index in range(1, 4)
        ]
        candidate = session_friction.find_candidates(events)[0]

        self.assertNotIn("abc123", candidate.sample)
        self.assertIn("<redacted>", candidate.sample)


if __name__ == "__main__":
    unittest.main()
