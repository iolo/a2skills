#!/usr/bin/env python3
"""Portable package and launcher checks; no toolchains, emulators, or ROMs."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from check import check_skill
from sync_references import sync

ROOT = Path(__file__).resolve().parents[1]


def load_script(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


package = load_script('package_disk', 'a2-a2kit/scripts/package_disk.py')
mame = load_script('mame_launch', 'a2-mame/scripts/launch.py')
gs2 = load_script('gs2_smoke', 'a2-gssquared/scripts/smoke.py')


class Packages(unittest.TestCase):
    def test_installed_copies_without_canonical_sources(self):
        with tempfile.TemporaryDirectory(prefix='a2 café 한글 ') as temporary:
            for entry in ROOT.glob('a2-*/SKILL.md'):
                with self.subTest(skill=entry.parent.name):
                    installed = Path(temporary) / entry.parent.name
                    shutil.copytree(entry.parent, installed, symlinks=False,
                                    ignore=shutil.ignore_patterns('__pycache__'))
                    check_skill(installed)

    def test_reference_drift_and_windows_symlink_placeholder(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'references'
            source.mkdir()
            (source / 'sample.md').write_text('# Sample café\n', encoding='utf-8')
            skill = root / 'a2-sample'
            (skill / 'references').mkdir(parents=True)
            (skill / 'SKILL.md').write_text(
                '---\nname: a2-sample\ndescription: Test\n---\n'
                '[Sample](references/sample.md)\n', encoding='utf-8')
            target = skill / 'references/sample.md'
            target.write_text('../../references/sample.md', encoding='utf-8')
            with self.assertRaisesRegex(AssertionError, 'placeholder'):
                check_skill(skill)
            self.assertEqual(len(sync(root)), 1)
            sync(root, write=True)
            self.assertFalse(target.is_symlink())
            self.assertEqual(target.read_bytes(), (source / 'sample.md').read_bytes())
            check_skill(skill)
            self.assertEqual(sync(root), [])
            target.write_text('# Outdated\n', encoding='utf-8')
            self.assertEqual(len(sync(root)), 1)

    def test_check_with_non_utf8_default_encoding(self):
        # Python 3.10/3.12 can still default to ASCII/legacy Windows encodings.
        # Source files must be read as UTF-8 independently of that default.
        result = subprocess.run(
            [sys.executable, str(ROOT / 'scripts/check.py')],
            env={**os.environ, 'PYTHONUTF8': '0', 'PYTHONCOERCECLOCALE': '0', 'LC_ALL': 'C'},
            capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))


class Tools(unittest.TestCase):
    def test_matching_bundle_architectures(self):
        for system, machine, directory, filename in (
            ('Darwin', 'x86_64', 'darwin-x86_64', 'a2kit'),
            ('Darwin', 'arm64', 'darwin-arm64', 'a2kit'),
            ('Windows', 'AMD64', 'windows-x86_64', 'a2kit.exe'),
            ('Windows', 'ARM64', 'windows-arm64', 'a2kit.exe'),
            ('Linux', 'aarch64', 'linux-arm64', 'a2kit'),
        ):
            with self.subTest(system=system, machine=machine):
                expected = str(ROOT / 'a2-a2kit/assets/tools' / directory / filename)
                with patch('platform.system', return_value=system), \
                     patch('platform.machine', return_value=machine), \
                     patch.object(package.shutil, 'which', side_effect=lambda p: p if p == expected else None):
                    self.assertEqual(package.resolve_tool(), expected)

    def test_explicit_missing_tool_does_not_fall_back(self):
        with patch.object(package.shutil, 'which', side_effect=lambda p: '/found/a2kit' if p == 'a2kit' else None):
            self.assertIsNone(package.resolve_tool('/missing/tool'))

    def test_unknown_arch_uses_path_not_legacy_bundle(self):
        with patch('platform.system', return_value='Darwin'), \
             patch('platform.machine', return_value='unknown'), \
             patch.object(package.shutil, 'which', side_effect=lambda p: p if p == 'a2kit' or p.endswith('a2kit-mac') else None):
            self.assertEqual(package.resolve_tool(), 'a2kit')


class Emulators(unittest.TestCase):
    def test_gs2_missing_socket_skips_before_launch(self):
        with patch.object(gs2, 'socket', SimpleNamespace()), \
             patch.object(sys, 'argv', ['smoke.py', '--output-dir', 'unused']), \
             patch.object(gs2.subprocess, 'Popen') as launch:
            self.assertEqual(gs2.main(), 77)
            launch.assert_not_called()

    def test_gs2_process_groups(self):
        with patch.object(gs2, 'os', SimpleNamespace(name='posix')):
            self.assertEqual(gs2.process_group_options(), {'start_new_session': True})
        with patch.object(gs2, 'os', SimpleNamespace(name='nt')), \
             patch.object(gs2.subprocess, 'CREATE_NEW_PROCESS_GROUP', 512, create=True):
            self.assertEqual(gs2.process_group_options(), {'creationflags': 512})

    def test_mame_launcher_plugin_paths_debugger_and_wait(self):
        with tempfile.TemporaryDirectory(prefix='a2 mame café ') as temporary:
            root = Path(temporary)
            executable = root / 'bin/mame.exe'
            # A Homebrew-like prefix, distinct from adjacent Windows plugins.
            plugins = root / 'share/mame/plugins'
            for plugin in ('console', 'json'):
                directory = plugins / plugin
                directory.mkdir(parents=True)
                (directory / 'init.lua').write_text('-- fixture\n', encoding='utf-8')
            for extra, expected in ((['--debug'], None), (['--debugger', 'windows'], 'windows'),
                                    (['--headless', '--debug'], 'qt')):
                with self.subTest(extra=extra):
                    out = root / ('session-' + str(len(list(root.glob('session-*')))))
                    fake_process = Mock()
                    fake_process.wait.return_value = 23
                    fake_os = SimpleNamespace(name='nt', environ={}, chdir=Mock())
                    argv = ['launch.py', '--rompath', str(root), '--output-dir', str(out), *extra]
                    with patch.object(sys, 'argv', argv), \
                         patch.object(mame, 'os', fake_os), \
                         patch.object(mame.shutil, 'which', return_value=str(executable)), \
                         patch.object(mame.subprocess, 'run') as audit, \
                         patch.object(mame.subprocess, 'Popen', return_value=fake_process) as launch:
                        self.assertEqual(mame.main(), 23)
                    command = launch.call_args.args[0]
                    self.assertIn('-verifyroms', audit.call_args.args[0])
                    self.assertEqual(command[command.index('-pluginspath') + 1], str(plugins.resolve()))
                    self.assertIn('-debug', command)
                    if expected:
                        self.assertEqual(command[command.index('-debugger') + 1], expected)
                    else:
                        self.assertNotIn('-debugger', command)
                    fake_process.wait.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)
