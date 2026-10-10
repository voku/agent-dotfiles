"""Exercise the Actions summary step with a real inconclusive report."""

from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest


class MutationWorkflowTest(unittest.TestCase):
    def test_inconclusive_report_is_published_and_preserves_failure(self):
        repository = Path(__file__).resolve().parents[1]
        workflow = (repository / '.github/workflows/mutation.yml').read_text()
        step = workflow.split('      - name: Generate evidence and summary\n        run: |\n', 1)[1]
        script = textwrap.dedent(step.split('      - name:', 1)[0])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'tools').mkdir()
            shutil.copyfile(repository / 'tools/mutation_report.py', root / 'tools/mutation_report.py')
            executable = root / 'cosmic-ray'
            executable.write_text('#!/bin/sh\nprintf \'%s\\n\' \'[{"mutations": []}, null]\'\n')
            executable.chmod(0o755)
            summary = root / 'step-summary.md'
            result = subprocess.run(
                ['bash', '-e', '-o', 'pipefail', '-c', script], cwd=root,
                env={**os.environ, 'PATH': str(root) + os.pathsep + os.environ['PATH'],
                     'GITHUB_STEP_SUMMARY': str(summary)}, capture_output=True, text=True,
            )
            self.assertEqual(1, result.returncode, result.stderr)
            self.assertTrue(summary.is_file(), 'Actions summary must survive reporter exit 1')
            self.assertEqual((root / 'mutation-summary.md').read_text(), summary.read_text())
            self.assertIn('Pending: 1', summary.read_text())


if __name__ == '__main__':
    unittest.main()
