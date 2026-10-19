#!/usr/bin/env python3
"""Offline mailbox failure/retry and launcher profile contracts; no ROMs required."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rpc = load('mame_rpc', 'a2-mame/scripts/rpc.py')
launcher = load('mame_launcher', 'a2-mame/scripts/launch.py')


class Mailbox(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='a2 mailbox café ')
        self.addCleanup(self.temp.cleanup)
        self.session = Path(self.temp.name)
        self.directory = self.session / 'mailbox'
        self.directory.mkdir()
        self.ready = self.directory / 'ready.json'
        self.ready.write_text('{"ok":true}', encoding='utf-8')

    def test_timeout_preserves_unaccepted_request(self):
        with self.assertRaisesRegex(TimeoutError, 'inspect request'):
            rpc.request(self.session, operation='go', timeout=0.05)
        before = (self.directory / 'request.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'earlier request is pending'):
            rpc.request(self.session, operation='go')
        self.assertEqual((self.directory / 'request.json').read_bytes(), before)
        self.assertFalse((self.directory / 'client.lock').exists())

    def test_accepted_without_receipt_blocks_then_exact_receipt_recovers(self):
        accepted = self.directory / 'previous.request.json'
        accepted.write_text('{"id":"previous","operation":"write"}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'accepted request has no receipt'):
            rpc.request(self.session, operation='go')
        (self.directory / 'previous.response.json').write_text('{"id":"previous","ok":true}', encoding='utf-8')
        self.reply_once({'ok': True, 'result': {'scheduled': 'go'}})
        receipt = rpc.request(self.session, operation='go')
        self.assertEqual(receipt['result'], {'scheduled': 'go'})
        self.assertTrue((self.directory / (receipt['id'] + '.request.json')).exists())

    def reply_once(self, response, mismatch=False):
        def worker():
            deadline = time.monotonic() + 2
            pending = self.directory / 'request.json'
            while not pending.exists():
                if time.monotonic() > deadline:
                    return
                time.sleep(0.005)
            value = json.loads(pending.read_text(encoding='utf-8'))
            pending.rename(self.directory / (value['id'] + '.request.json'))
            data = {**response, 'id': 'wrong' if mismatch else value['id']}
            temporary = self.directory / 'reply.tmp'
            temporary.write_text(json.dumps(data), encoding='utf-8')
            temporary.rename(self.directory / (value['id'] + '.response.json'))
        thread = threading.Thread(target=worker)
        thread.start()
        self.addCleanup(thread.join, 3)

    def test_startup_failure_terminal_and_no_request(self):
        self.ready.write_text('{"ok":false,"error":"bad adapter"}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'startup failed'):
            rpc.request(self.session, code='return 42')
        self.assertFalse((self.directory / 'request.json').exists())

    def test_live_lock_and_terminal_transport_error(self):
        lock = self.directory / 'client.lock'
        lock.write_text('live client', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Another mailbox client'):
            rpc.request(self.session, operation='status')
        self.assertEqual(lock.read_text(encoding='utf-8'), 'live client')
        lock.unlink()
        (self.directory / 'transport-error.json').write_text('{"error":"I/O failure"}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Terminal mailbox failure'):
            rpc.request(self.session, operation='status')

    def test_lua_error_is_receipt_and_mismatched_id_is_rejected(self):
        self.reply_once({'ok': False, 'error': 'syntax error'})
        self.assertFalse(rpc.request(self.session, code=')')['ok'])
        self.reply_once({'ok': True}, mismatch=True)
        with self.assertRaisesRegex(ValueError, 'Mismatched mailbox receipt'):
            rpc.request(self.session, operation='status')


class Launcher(unittest.TestCase):
    def test_cffa_copies_media_records_hashes_and_no_stdin(self):
        with tempfile.TemporaryDirectory(prefix='a2 profile café ') as temporary:
            root = Path(temporary)
            plugins = root / 'plugins'
            for name in ('console', 'json'):
                (plugins / name).mkdir(parents=True)
                (plugins / name / 'init.lua').write_text('-- fixture', encoding='utf-8')
            disk = root / 'original.po'
            disk.write_bytes(b'raw media bytes')
            firmware = root / 'cffa20ee02.bin'
            firmware.write_bytes(b'local firmware')
            out = root / 'session'
            process = Mock(pid=6789)
            process.wait.return_value = 0
            argv = ['launch.py', '--rompath', str(root), '--pluginspath', str(plugins),
                    '--transport', 'mailbox', '--profile', 'iie-cffa', '--headless', '--fast',
                    '--disk', str(disk), '--cffa-rom', str(firmware), '--output-dir', str(out)]
            with patch.object(sys, 'argv', argv), \
                 patch.object(launcher.shutil, 'which', return_value=str(root / 'mame')), \
                 patch.object(launcher.subprocess, 'run') as audit, \
                 patch.object(launcher.subprocess, 'Popen', return_value=process) as launch:
                self.assertEqual(launcher.main(), 0)
            command = launch.call_args.args[0]
            self.assertIn('-hard1', command)
            self.assertIn('-noconsole', command)
            self.assertIn('-nothrottle', command)
            self.assertIn('-noreadconfig', command)
            self.assertNotIn('-aviwrite', command)
            self.assertNotIn('-flop1', command)
            self.assertEqual(command[1], 'apple2e')
            self.assertEqual(launch.call_args.kwargs['stdin'], launcher.subprocess.DEVNULL)
            self.assertEqual((out / 'media.hdv').read_bytes(), disk.read_bytes())
            self.assertEqual([call.args[0][1] for call in audit.call_args_list], ['apple2e', 'a2cffa02'])
            self.assertTrue(json.loads((out / 'exit.json').read_text(encoding='utf-8'))['source_unchanged'])
            self.assertEqual(json.loads((out / 'session.json').read_text(encoding='utf-8'))['command'], command)
            if os.name == 'posix':
                self.assertEqual(out.stat().st_mode & 0o777, 0o700)

    def test_timeout_terminates_owned_child_and_records_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ('console', 'json'):
                (root / name).mkdir()
                (root / name / 'init.lua').write_text('-- fixture', encoding='utf-8')
            process = Mock(pid=1234)
            process.wait.side_effect = [launcher.subprocess.TimeoutExpired('mame', 1), 0]
            out = root / 'session'
            argv = ['launch.py', '--rompath', str(root), '--pluginspath', str(root),
                    '--output-dir', str(out), '--timeout', '1']
            with patch.object(sys, 'argv', argv), \
                 patch.object(launcher.shutil, 'which', return_value=str(root / 'mame')), \
                 patch.object(launcher.subprocess, 'run'), \
                 patch.object(launcher.subprocess, 'Popen', return_value=process):
                self.assertEqual(launcher.main(), 124)
            process.terminate.assert_called_once()
            self.assertEqual(json.loads((out / 'exit.json').read_text(encoding='utf-8'))['reason'], 'timeout')


if __name__ == '__main__':
    unittest.main(verbosity=2)
