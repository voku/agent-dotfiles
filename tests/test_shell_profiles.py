"""Actual Bash/Zsh consumer contracts, including hostile-looking filenames."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parent.parent
ASSETS = ('.bashrc', '.zshrc', '.shellrc', '.exports', '.functions',
          'shell/modules/context.sh', 'shell/modules/git.sh')


class ShellProfilesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.home = self.root / 'agent tools [雪]\\literal\n'
        self.home.mkdir()
        for name in ASSETS:
            target = self.home / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PROJECT / name, target)
        (self.home / 'bin').mkdir()
        self.binary = self.home / 'bin/agent-dotfiles'
        self.binary.write_text(f'#!{sys.executable}\nimport json,os,sys\nprint(json.dumps(sys.argv[1:]))\nsys.exit(int(os.environ.get("FIXTURE_EXIT", "0")))\n')
        self.binary.chmod(0o755)
        self.user = self.root / 'user'
        self.user.mkdir()
        for name in ('.bashrc', '.bash_profile', '.zshrc', '.zprofile'):
            (self.user / name).write_text(f'touch "{self.root}/unsafe-startup"\n')

    def shells(self):
        for shell, profile in [('bash', '.bashrc'), ('zsh', '.zshrc')]:
            executable = shutil.which(shell)
            if executable:
                yield executable, profile
        if not shutil.which('bash'):
            self.fail('Actual Bash validation is required')
        if os.environ.get('REQUIRE_ZSH') and not shutil.which('zsh'):
            self.fail('CI requires actual Zsh validation')

    def run_shell(self, shell, profile, script, args=(), environment=None):
        flags = ['--noprofile', '--norc'] if Path(shell).name == 'bash' else ['-f']
        env = {**os.environ, 'HOME': str(self.user)}
        env.pop('AGENT_DOTFILES_HOME', None)
        env.update(environment or {})
        env.pop("BASH_ENV", None)  # Bash startup occurs before our explicit profile.
        return subprocess.run([shell, *flags, '-c', script, 'consumer', str(self.home / profile), *args],
                              cwd=self.root, env=env, capture_output=True, text=True, timeout=15)

    def test_silent_activation_preserves_state_and_deactivation(self):
        for shell, profile in self.shells():
            with self.subTest(shell=shell):
                result = self.run_shell(shell, profile, '''
set -eu
before_options=$-
before_path=$PATH
before_pwd=$PWD
before_args=$#
. "$1"
[ "$before_options" = "$-" ]
[ "$before_path" = "$PATH" ]
[ "$before_pwd" = "$PWD" ]
[ "$before_args" = "$#" ]
[ "$2" = 'space λ' ]
[ "$AGENT_DOTFILES_HOME" = "$3" ]
agent_deactivate
[ "${AGENT_DOTFILES_HOME+x}" != x ]
! typeset -f agent_search >/dev/null 2>&1
''', ('space λ', str(self.home)), {'CDPATH': str(self.root)})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, '')
                self.assertEqual(result.stderr, '')
                self.assertFalse((self.root / 'unsafe-startup').exists())

    def test_fresh_consumer_blocks_inherited_bash_startup(self):
        startup = self.root / 'inherited-startup.sh'
        marker = self.root / 'unsafe-inherited-startup'
        startup.write_text(f'touch "{marker}"\n')
        for shell, profile in self.shells():
            result = self.run_shell(shell, profile, '. "$1"; agent_doctor', environment={'BASH_ENV': str(startup)})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(marker.exists(), 'Inherited BASH_ENV executed before explicit activation')

    def test_wrappers_preserve_argv_and_nonzero_exit(self):
        mapping = {'agent_search': 'search', 'agent_read': 'read', 'agent_patch': 'git-patch',
                   'agent_status': 'git-status', 'agent_files': 'files',
                   'agent_tracked': 'tracked', 'agent_doctor': 'doctor'}
        args = ['--', 'spaces λ', 'line\nname', '[literal]*', '-leading', '']
        for shell, profile in self.shells():
            for helper, command in mapping.items():
                with self.subTest(shell=shell, helper=helper):
                    result = self.run_shell(shell, profile, '. "$1"; shift; helper=$1; shift; "$helper" "$@"',
                                            (helper, *args), {'FIXTURE_EXIT': '3'})
                    self.assertEqual(result.returncode, 3, result.stderr)
                    self.assertEqual(json.loads(result.stdout), [command, *args])

    def test_collision_and_missing_assets_refuse_activation(self):
        for shell, profile in self.shells():
            for script in ['agent_search() { printf original; }; . "$1"',
                           'AGENT_DOTFILES_HOME=existing; . "$1"',
                           'alias agent_read="printf original"; . "$1"']:
                result = self.run_shell(shell, profile, script)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn('agent-dotfiles:', result.stderr)
        (self.home / '.functions').unlink()
        for shell, profile in self.shells():
            result = self.run_shell(shell, profile, '. "$1"')
            self.assertEqual(result.returncode, 2)
            self.assertIn('.functions', result.stderr)
        shutil.copyfile(PROJECT / '.functions', self.home / '.functions')
        (self.home / 'shell/modules/context.sh').unlink()
        for shell, profile in self.shells():
            result = self.run_shell(shell, profile, '. "$1"')
            self.assertEqual(result.returncode, 2)
            self.assertIn('shell/modules/context.sh', result.stderr)

    def test_removed_executable_is_visible_failure(self):
        for shell, profile in self.shells():
            result = self.run_shell(shell, profile, '. "$1"; command rm -- "$AGENT_DOTFILES_HOME/bin/agent-dotfiles"; agent_read example')
            self.assertIn(result.returncode, (126, 127))
            self.assertTrue(result.stderr)
            self.binary.write_text('#!/bin/sh\nexit 0\n')
            self.binary.chmod(0o755)

    def test_native_history_and_blame_argv(self):
        git = self.home / 'bin/git'
        git.write_text(f'#!{sys.executable}\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n')
        git.chmod(0o755)
        for shell, profile in self.shells():
            for helper, operation, extra in [('agent_history', 'log', []), ('agent_blame', 'blame', ['--line-porcelain'])]:
                result = self.run_shell(shell, profile, '. "$1"; "$2" -- "$3"', (helper, 'path [λ]\n'),
                                        {'PATH': str(git.parent) + os.pathsep + os.environ['PATH']})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), ['--no-pager', '--literal-pathspecs', '-c', 'color.ui=false', operation, *extra, '--', 'path [λ]\n'])

    def test_real_checkout_source_evidence(self):
        source = self.root / 'literal [λ]\n.py'
        source.write_bytes(b'first\nsecond\n')
        for shell, profile in self.shells():
            self.home = PROJECT
            result = self.run_shell(shell, profile, '. "$1"; agent_read "$2" --root "$3" --start 2 --end 2',
                                    (source.name, str(self.root)))
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report['schema'], 'agent-dotfiles.v1.read')
            self.assertEqual(report['content'], 'second\n')


if __name__ == '__main__':
    unittest.main()
