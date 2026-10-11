"""Reject misleading identity even when the original source bytes match."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from tools import real_php_preflight as preflight


class RealPhpPreflightTest(unittest.TestCase):
    def payload(self):
        source = b"<?php\n" * 10
        return source, {
            "schema": "agent-dotfiles.v1.read", "root": "/fixture/php",
            "path": preflight.SOURCE, "start": 1, "requested_end": 8,
            "actual_end": 8, "sha256": hashlib.sha256(source).hexdigest(),
            "content": "<?php\n" * 8, "content_bytes": 48, "truncated": False,
        }

    def test_valid_original_source_identity(self):
        source, payload = self.payload()
        preflight.check_read(json.dumps(payload).encode(), source, Path("/fixture/php"))

    def test_wrong_identity_is_rejected_with_identical_bytes(self):
        for key, wrong in (("path", "WRONG.php"), ("root", "/another/php"),
                           ("requested_end", 999)):
            with self.subTest(key=key):
                source, payload = self.payload()
                payload[key] = wrong
                with self.assertRaises(AssertionError):
                    preflight.check_read(json.dumps(payload).encode(), source,
                                         Path("/fixture/php"))

    def test_failed_verify_still_attempts_safe_uninstall(self):
        workflow = (Path(__file__).resolve().parents[1] /
                    ".github/workflows/real-php-preflight.yml").read_text()
        block = workflow.split("      - name: Verify after use", 1)[1]
        script = block.split("        run: |\n", 1)[1].split("\n      - name:", 1)[0]
        script = "\n".join(line[10:] for line in script.splitlines())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "dotfiles").mkdir()
            (root / "agent-dotfiles-consumer").mkdir()
            installer = root / "dotfiles/install.sh"
            installer.write_text('#!/bin/sh\nprintf "%s\\n" "$1" >> calls\n'
                                 'if [ "$1" = verify ]; then exit 2; fi\nexit 0\n')
            installer.chmod(0o755)
            result = subprocess.run(["bash", "-c", script], cwd=root,
                                    env={"RUNNER_TEMP": str(root), "DOTFILES_SHA": "a" * 40},
                                    capture_output=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((root / "calls").read_text().splitlines(),
                             ["verify", "uninstall"])

    def test_project_onboarding_rejects_non_object_composer_scripts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "composer.json").write_text('{"name":"fixture","scripts":[]}')
            with self.assertRaises(AssertionError):
                preflight.project_onboarding(root, b"skill")


if __name__ == "__main__":
    unittest.main()
