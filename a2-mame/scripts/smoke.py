#!/usr/bin/env python3
"""Optional real MAME Lua integration test (POSIX PTY); exit 77 means SKIP."""
import argparse
import json
import os
from pathlib import Path
import re
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import time


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mame', default='mame')
    p.add_argument('--rompath', type=Path)
    p.add_argument('--pluginspath', type=Path)
    p.add_argument('--driver', choices=('apple2', 'apple2e', 'apple2ee'), default='apple2')
    p.add_argument('--disk', type=Path, help='optional mount/eject test; only a copy is mounted')
    args = p.parse_args()
    if os.name != 'posix' or not shutil.which(args.mame) or not args.rompath:
        print('SKIP: requires POSIX, MAME, and --rompath'); return 77
    audit = subprocess.run([args.mame, args.driver, '-noreadconfig', '-rompath', str(args.rompath), '-verifyroms'],
                           capture_output=True, text=True, timeout=30)
    if audit.returncode:
        print('SKIP: ROM audit failed\n' + audit.stdout + audit.stderr); return 77
    import pty
    scripts = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix='a2-mame-test-') as temporary:
        root = Path(temporary)
        raw = root / 'marker.bin'
        raw.write_bytes(bytes.fromhex('2c51c02c54c0a9c18d0004a9428d00034c1008'))
        master, slave = pty.openpty()
        command = [sys.executable, str(scripts / 'launch.py'), '--mame', args.mame,
                   '--driver', args.driver, '--rompath', str(args.rompath.resolve()),
                   '--output-dir', str(root / 'session'), '--headless', '--debugger', 'qt']
        if args.pluginspath:
            command += ['--pluginspath', str(args.pluginspath.resolve())]
        process = subprocess.Popen(command, stdin=slave, stdout=slave, stderr=slave,
                                   start_new_session=True, env={**os.environ, 'TERM': 'dumb'})
        os.close(slave)
        transcript = ''
        pending = ''
        sequence = 0

        def send(line):
            os.write(master, (line + '\n').encode())

        def until(predicate, timeout=8):
            nonlocal transcript, pending
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if predicate():
                    return
                if process.poll() is not None:
                    raise RuntimeError(f'MAME exited {process.returncode}: {transcript[-3000:]}')
                if select.select([master], [], [], 0.1)[0]:
                    try:
                        chunk = os.read(master, 65536).decode(errors='replace')
                    except OSError as error:
                        raise RuntimeError(transcript[-3000:]) from error
                    transcript = (transcript + chunk)[-20000:]
                    pending = (pending + re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', chunk))[-20000:]
            raise TimeoutError('bounded MAME wait expired: ' + transcript[-2000:])

        def call(operation, *values):
            nonlocal sequence, pending
            sequence += 1
            ident = str(sequence)
            pending = ''
            encoded = ','.join(json.dumps(v, ensure_ascii=False) for v in values)
            send(f'a2.call("{ident}","{operation}"' + (',' + encoded if encoded else '') + ')')
            result = []

            def received():
                for match in re.finditer(r'A2 (\{[^\r\n]+\})', pending):
                    try:
                        obj = json.loads(match.group(1))
                    except ValueError:
                        continue
                    if obj.get('id') == ident:
                        result.append(obj); return True
                return False
            until(received)
            assert result[0]['ok'], result[0]
            return result[0]['result']

        def wait_stop():
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                if call('status')['debugger'] == 'stop':
                    return
                time.sleep(0.05)
            raise TimeoutError('no debugger stop')

        try:
            until(lambda: '[MAME]' in pending)
            send('a2 = dofile(' + json.dumps((scripts / 'control.lua').as_posix(), ensure_ascii=False) + ')')
            assert call('status')['driver'] == args.driver
            call('devices')
            call('pause')
            original_sp = call('registers')['SP']
            assert call('set_register', 'SP', 511)['SP'] == 511
            call('set_register', 'SP', original_sp)
            assert call('load_binary', str(raw), 2048)['bytes'] == list(raw.read_bytes())
            call('set_register', 'PC', 2048)
            bp = call('breakpoint', 2064)['id']
            call('go'); wait_stop()
            assert call('registers')['PC'] == 2064
            assert call('read', 768, 1)['bytes'] == [66]
            assert call('read', 1024, 1)['bytes'] == [193]
            assert call('clear_breakpoint', bp)['cleared']
            call('step'); wait_stop()
            assert call('registers')['PC'] == 2064
            screen = root / 'screen.png'
            call('screenshot', str(screen))
            assert screen.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
            # Queued input: a tiny raw loop consumes the keyboard latch.
            keyprog = root / 'keys.bin'
            keyprog.write_bytes(bytes.fromhex('ad00c010fb8d01032c10c04c0009'))
            call('load_binary', str(keyprog), 2304)
            call('set_register', 'PC', 2304)
            call('go')
            call('keys', 'A')
            deadline = time.monotonic() + 5
            while True:
                call('pause')
                value = call('read', 769, 1)['bytes'][0]
                if value == 193:
                    break
                assert time.monotonic() < deadline, 'keyboard not consumed'
                call('resume'); time.sleep(0.1)
            call('resume')
            state = root / 'scratch.sta'
            call('save', str(state))
            until(lambda: state.exists() and state.stat().st_size > 0)
            call('pause')
            # Use native Lua table syntax, not JSON arrays, for explicit writes.
            send('a2.write(769,{0})')
            assert call('read', 769, 1)['bytes'] == [0]
            call('restore', str(state)); call('resume')
            deadline = time.monotonic() + 5
            while True:
                call('pause')
                if call('read', 769, 1)['bytes'] == [193]:
                    break
                assert time.monotonic() < deadline, 'state restore did not complete'
                call('resume'); time.sleep(0.1)
            if args.disk:
                disk = root / ('disk' + args.disk.suffix)
                shutil.copyfile(args.disk, disk)
                devices = call('devices')
                tag = next(i['tag'] for i in devices['images'] if i['instance'] == 'floppydisk1')
                assert call('mount', tag, str(disk))['filename'] == str(disk)
                call('eject', tag)
            call('exit')
            # Wake linenoise's pending console read during process teardown.
            send('')
            process.wait(timeout=8)
            assert process.returncode == 0, process.returncode
            print(f'PASS: {args.driver} Lua load, memory, breakpoint, step, input, screenshot, save/restore, cleanup')
            return 0
        except Exception:
            print(transcript[-3000:], file=sys.stderr)
            raise
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL); process.wait()
            os.close(master)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (AssertionError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        sys.exit('FAIL: ' + str(error))
