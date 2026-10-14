#!/usr/bin/env python3
"""Build and package real fixtures from isolated installed skill copies."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Workflows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for tool in ('cl65', 'ca65', 'ld65', 'a2kit'):
            if not shutil.which(tool):
                raise RuntimeError(f'{tool} required for offline workflow tests')
        cls.temp = tempfile.TemporaryDirectory(prefix='a2 workflow ')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        for skill in ('a2-basic', 'a2-cc65', 'a2-a2kit'):
            shutil.copytree(ROOT / skill, cls.root / skill, symlinks=False)
        cls.build = cls.root / 'a2-cc65/scripts/build_examples.py'
        cls.pack = cls.root / 'a2-a2kit/scripts/package_disk.py'
        cls.native = cls.root / 'native build'
        cls.run_command(sys.executable, cls.build, '--output-dir', cls.native)

    @staticmethod
    def run_command(*args, success=True, input=None):
        result = subprocess.run(list(map(str, args)), input=input, capture_output=True, timeout=60)
        if success and result.returncode != 0:
            raise AssertionError(result.stderr.decode(errors='replace'))
        if not success and result.returncode == 0:
            raise AssertionError('unexpected success')
        return result

    def package(self, fmt, src, base, out, name='TESTPROG', extra=(), success=True):
        return self.run_command(sys.executable, self.pack, '--source', src, '--format', fmt,
                                '--base-image', base, '--output-dir', out, '--name', name,
                                *extra, success=success)

    def test_native_and_basic_on_both_filesystems(self):
        fixtures = [('basic', self.root / 'a2-basic/assets/examples/hello.bas', ()),
                    ('raw', self.native / 'hello.bin', ('--address', '0x800')),
                    ('applesingle', self.native / 'hello.as', ()),
                    ('applesingle', self.native / 'mixed.as', ())]
        for filename in ('dos-3.3.dsk', 'prodos-2.4.3.po'):
            base = ROOT / 'assets' / filename
            before = base.read_bytes()
            for index, (fmt, source, extra) in enumerate(fixtures):
                with self.subTest(disk=filename, format=fmt, source=source.name):
                    out = self.root / f'{filename}-{index}'
                    self.package(fmt, source, base, out, extra=extra)
                    manifest = json.loads((out / 'manifest.json').read_text(encoding='utf-8'))
                    payload = (out / 'payload.bin').read_bytes()
                    self.assertEqual(manifest['payload_sha256'], hashlib.sha256(payload).hexdigest())
                    if fmt == 'basic':
                        retokenized = self.run_command('a2kit', 'tokenize', '-t', 'atxt', '-a', '2049',
                                                      input=(out / 'listing.bas').read_bytes()).stdout
                        self.assertEqual(payload, retokenized)
                    if fmt == 'raw':
                        self.assertEqual(payload, source.read_bytes())
                    self.assertEqual(before, base.read_bytes())

    def test_reject_overwrites_and_missing_tools(self):
        source = self.native / 'hello.bin'
        base = ROOT / 'assets/dos-3.3.dsk'
        out = self.root / 'preserve'
        out.mkdir(); (out / 'sentinel').write_text('unchanged')
        self.package('raw', source, base, out, extra=('--address', '2048'), success=False)
        self.assertEqual((out / 'sentinel').read_text(), 'unchanged')
        self.package('raw', source, base, self.root / 'collision', name='HELLO', extra=('--address', '2048'), success=False)
        self.package('raw', source, base, self.root / 'no-tool', extra=('--address', '2048', '--a2kit', '/missing/tool'), success=False)
        self.run_command(sys.executable, self.build, '--output-dir', self.root / 'no-build', '--cl65', '/missing/tool', success=False)
        self.run_command(sys.executable, self.build, '--output-dir', self.native, success=False)
        self.run_command(sys.executable, self.build, '--output-dir', self.root / 'a2-cc65/assets/examples/nested', success=False)

    def test_invalid_sources(self):
        base = ROOT / 'assets/dos-3.3.dsk'
        empty = self.root / 'empty'; empty.write_bytes(b'')
        bad = self.root / 'invalid.as'; bad.write_bytes(b'not AppleSingle')
        self.package('raw', empty, base, self.root / 'empty-out', extra=('--address', '2048'), success=False)
        self.package('applesingle', bad, base, self.root / 'bad-as', success=False)
        self.package('raw', self.native / 'hello.bin', base, self.root / 'overflow', extra=('--address', '65535'), success=False)
        self.package('raw', self.native / 'hello.bin', base, self.root / 'no-address', success=False)

    def test_unicode_paths_and_crlf_basic(self):
        directory = self.root / 'disk space café 한글'
        directory.mkdir()
        base = directory / 'boot disk.po'
        shutil.copyfile(ROOT / 'assets/prodos-2.4.3.po', base)
        source = directory / 'hello café.bas'
        listing = (self.root / 'a2-basic/assets/examples/hello.bas').read_bytes()
        source.write_bytes(listing.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
        out = directory / 'packaged disk'
        # Exercise redirected CLI output with an explicitly legacy encoding,
        # even on Linux. The helper's path output must still be valid UTF-8.
        result = subprocess.run(
            [sys.executable, str(self.pack), '--source', str(source), '--format', 'basic',
             '--base-image', str(base), '--output-dir', str(out), '--name', 'TESTPROG'],
            env={**os.environ, 'PYTHONIOENCODING': 'cp1252'}, capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))
        self.assertIn(str(out), result.stdout.decode('utf-8'))
        expected = self.run_command('a2kit', 'tokenize', '-t', 'atxt', '-a', '2049', input=listing).stdout
        self.assertEqual((out / 'payload.bin').read_bytes(), expected)

    @unittest.skipUnless(shutil.which('ac'), 'AppleCommander optional')
    def test_applecommander_basic_equivalent(self):
        disk = self.root / 'ac.dsk'
        shutil.copyfile(ROOT / 'assets/dos-3.3.dsk', disk)
        source = (self.root / 'a2-basic/assets/examples/hello.bas').read_bytes()
        self.run_command('ac', '-bas', disk, 'DEMOBAS', input=source)
        exported = self.run_command('ac', '-e', disk, 'DEMOBAS').stdout
        tokens = self.run_command('a2kit', 'get', '-d', disk, '-f', 'DEMOBAS', '-t', 'atok').stdout
        expected = self.run_command('a2kit', 'tokenize', '-t', 'atxt', '-a', '2049', input=source).stdout
        self.assertIn(b'APPLE II BASIC READY', exported)
        self.assertEqual(tokens, expected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
