#!/usr/bin/env python3
"""Launch an owned native GSSquared and verify debug-protocol behavior.

Requires upstream gs2debug (installed, or --client-src), an installed emulator
with assets, and a working native display. No downloads or user-session attach.
"""
import argparse
from collections import deque
import importlib
import json
import os
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import sys
import time


def process_group_options():
    if os.name == 'nt':
        return {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP}
    return {'start_new_session': True}


def socket_unavailable():
    """Probe the transport required by the upstream Python client before launch."""
    if not hasattr(socket, 'AF_UNIX'):
        return 'this Python runtime has no AF_UNIX; use a compatible runtime/client or configured MCP sidecar'
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM):
            pass
    except OSError as error:
        return f'AF_UNIX unavailable: {error}'
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emulator', default='GSSquared')
    parser.add_argument('--client-src', type=Path,
                        help='upstream clients/python/src directory')
    parser.add_argument('--platform', type=int, choices=range(6), default=3)
    parser.add_argument('--output-dir', type=Path, required=True,
                        help='new directory for socket, logs, and media copy')
    parser.add_argument('--disk', type=Path, help='optional image copied before mounting')
    parser.add_argument('--slot', type=int, default=6)
    parser.add_argument('--unit', type=int, default=0, help='0-based protocol unit')
    args = parser.parse_args()

    unavailable = socket_unavailable()
    if unavailable:
        print('SKIP: ' + unavailable, file=sys.stderr)
        return 77

    executable = shutil.which(args.emulator)
    if executable is None:
        print('SKIP: GSSquared executable not found', file=sys.stderr)
        return 77
    if args.client_src:
        sys.path.insert(0, str(args.client_src.resolve()))
    sys.dont_write_bytecode = True  # do not write into the supplied client checkout
    try:
        api = importlib.import_module('gs2debug')
    except ModuleNotFoundError as error:
        if error.name != 'gs2debug':
            raise
        print('SKIP: install upstream gs2debug or supply --client-src', file=sys.stderr)
        return 77
    if args.disk and not args.disk.is_file():
        parser.error('--disk must be an existing file')
    if not 0 <= args.slot <= 7 or not 0 <= args.unit <= 5:
        parser.error('slot must be 0..7 and unit 0..5')
    output = args.output_dir.resolve()
    socket_path = output / 'debug.sock'
    if len(str(socket_path).encode()) > 100:
        parser.error('use a shorter output path for AF_UNIX')
    output.mkdir(parents=True, exist_ok=False)
    disk = None
    if args.disk:
        disk = output / ('media' + args.disk.suffix)
        shutil.copy2(args.disk, disk)

    class BoundedClient(api.Client):
        def request(self, type_word, payload=b'', *, timeout=5.0):
            return super().request(type_word, payload, timeout=timeout)

    client = BoundedClient()
    stops = deque()

    def capture(event_id, seq, data):
        if event_id == api.EVT_STOPPED:
            stops.append(data)

    def stopped(reason, bp_id=None):
        # request() dispatches events received before its reply; do not lose them.
        deadline = time.monotonic() + 5.0
        while True:
            while stops:
                data = stops.popleft()
                if len(data) < 32:
                    raise RuntimeError('short stop event')
                got_reason, got_bp, pc = struct.unpack_from('<III', data)
                if got_reason == reason and (bp_id is None or bp_id == got_bp):
                    return pc
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('expected stop did not arrive')
            client.wait_event(timeout=remaining)

    client.on_event(capture)
    process = None
    connected = False
    bp = None
    checks = []
    result = 1
    with (output / 'emulator.log').open('w', encoding='utf-8') as log:
        try:
            process = subprocess.Popen(
                [str(Path(executable).absolute()), '--debug', str(socket_path),
                 '--no-quit-confirm', '-p', str(args.platform), '-s'],
                cwd=output, stdout=log, stderr=subprocess.STDOUT,
                **process_group_options())
            deadline = time.monotonic() + 15.0
            while True:
                if process.poll() is not None:
                    raise RuntimeError('emulator exited during startup; inspect emulator.log')
                try:
                    client.connect(str(socket_path))
                    connected = True
                    break
                except (FileNotFoundError, ConnectionRefusedError):
                    if time.monotonic() >= deadline:
                        raise TimeoutError('debug socket not ready')
                    time.sleep(0.05)
            assert client.hello().version == 1
            client.ping()
            while True:
                try:
                    status = client.get_status()
                    break
                except api.ProtocolError as error:
                    if error.message != 'no machine' or time.monotonic() >= deadline:
                        raise
                    time.sleep(0.05)
            assert status.platform_id == args.platform
            # Platform identity can be available before reset/device initialization
            # finishes. Wait for actual guest instructions before changing state.
            while not client.get_trace(count=1).entries:
                if time.monotonic() >= deadline:
                    raise TimeoutError('guest instruction trace not ready')
                time.sleep(0.05)
            checks.append('hello/status/ping')
            client.pause()
            stopped(api.STOP_PAUSE)
            assert client.get_status().execution_mode == 2

            # Bare 6502 fixture: LDA #$42; STA $0300; JMP $0805.
            # Explicit emulation mode/8-bit widths for the 65816 profiles.
            code = bytes.fromhex('a9 42 8d 00 03 4c 05 08')
            client.write_mem(api.MEM_MAIN_RAW, 0x0800, code)
            client.write_mem(api.MEM_MAIN_RAW, 0x0300, b'\x00')
            assert client.read_mem(api.MEM_MAIN_RAW, 0x0800, len(code)) == code
            assert 0x0800 in client.find_mem(api.MEM_MAIN_RAW, 0x0800, len(code), code)
            mask = api.REG_PC | api.REG_P
            registers = dict(pc=0x0800, p=0x34)
            if args.platform in (4, 5):
                mask |= api.REG_PB | api.REG_DB | api.REG_D | api.REG_E
                registers.update(pb=0, db=0, d=0, e=1)
            client.set_regs(mask, **registers)
            assert struct.unpack_from('<H', client.get_regs(), 16)[0] == 0x0800
            checks.append('physical memory/find/registers')
            bp = client.bp_set(kind=api.BP_KIND_EXEC, address=0x0805)
            assert any(item.id == bp for item in client.bp_list())
            stops.clear()
            client.continue_()
            assert stopped(api.STOP_BP_EXEC, bp) == 0x0805
            assert client.read_mem(api.MEM_MAIN_RAW, 0x0300, 1) == b'\x42'
            checks.append('execution breakpoint/guest marker')
            client.bp_clear(bp)
            bp = None
            stops.clear()
            client.step_into(1)
            assert stopped(api.STOP_STEP) == 0x0805
            assert client.get_trace(count=1).entries
            checks.append('step completion/trace')

            text_domain = api.MEM_MEGAII_RAW if args.platform == 5 else api.MEM_MAIN_RAW
            client.write_mem(text_domain, 0x0400, b'\xc1')
            screen = client.video_text(page=1, mode=api.VIDEO_MODE_TEXT40)
            assert screen.cols == 40 and len(screen.chars) == 960
            assert screen.as_lines()[0].startswith('A')
            checks.append('text snapshot')
            if disk:
                assert client.mount(args.slot, args.unit, str(disk)) == api.MEDIA_OK
                assert client.unmount(args.slot, args.unit) == api.MEDIA_OK
                checks.append('copied media mount/unmount')
            result = 0
        except Exception as error:
            print(f'FAIL: {type(error).__name__}: {error}', file=sys.stderr)
        finally:
            if connected:
                if bp is not None:
                    try:
                        client.bp_clear(bp)
                    except Exception:
                        pass
                try:
                    client.quit()
                except Exception as error:
                    print(f'FAIL: protocol quit: {error}', file=sys.stderr)
                    result = 1
                client.close()
            if process is not None:
                try:
                    exit_code = process.wait(timeout=5)
                    if exit_code != 0:
                        result = 1
                        print(f'FAIL: emulator exit {exit_code}', file=sys.stderr)
                except subprocess.TimeoutExpired:
                    result = 1
                    process.terminate()  # owned process launched with --no-quit-confirm
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
                    print('FAIL: emulator required forced cleanup', file=sys.stderr)
    report = dict(result='PASS' if result == 0 else 'FAIL', platform=args.platform,
                  checks=checks, log=str(output / 'emulator.log'))
    (output / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))
    return result


if __name__ == '__main__':
    sys.exit(main())
