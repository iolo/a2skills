#!/usr/bin/env python3
"""Real MAME mailbox/automation checks without a PTY; exit 77 means missing prerequisites."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from rpc import request


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mame', default='mame')
    p.add_argument('--rompath', type=Path)
    p.add_argument('--pluginspath', type=Path)
    p.add_argument('--driver', default='apple2', choices=('apple2', 'apple2e', 'apple2ee'))
    p.add_argument('--profile', default='floppy', choices=('floppy', 'iie-cffa'))
    p.add_argument('--cffa-rom', type=Path)
    p.add_argument('--disk', type=Path)
    p.add_argument('--output-dir', type=Path, help='new directory to retain evidence; otherwise temporary')
    args = p.parse_args()
    if not shutil.which(args.mame) or not args.rompath:
        print('SKIP: requires MAME and --rompath'); return 77
    driver = 'apple2e' if args.profile == 'iie-cffa' else args.driver
    audit = subprocess.run([args.mame, driver, '-noreadconfig', '-rompath', str(args.rompath), '-verifyroms'],
                           capture_output=True, text=True, timeout=30)
    if audit.returncode:
        print('SKIP: ROM audit failed\n' + audit.stdout + audit.stderr); return 77
    temporary = tempfile.TemporaryDirectory(prefix='a2-mailbox-test-') if not args.output_dir else None
    root = Path(temporary.name) if temporary else args.output_dir.resolve()
    if not temporary:
        root.mkdir(parents=True, exist_ok=False)
    scripts = Path(__file__).resolve().parent
    session = root / 'session'
    command = [sys.executable, str(scripts / 'launch.py'), '--mame', args.mame,
               '--driver', driver, '--profile', args.profile, '--rompath', str(args.rompath.resolve()),
               '--output-dir', str(session), '--transport', 'mailbox', '--headless', '--fast', '--timeout', '90']
    for name in ('pluginspath', 'cffa_rom', 'disk'):
        value = getattr(args, name)
        if value:
            command += ['--' + name.replace('_', '-'), str(value.resolve())]
    receipts = []
    process = subprocess.Popen(command, stdin=subprocess.DEVNULL)

    def rpc(operation=None, *values, code=None, ok=True):
        result = request(session, operation=operation, args=list(values), code=code)
        receipts.append(result)
        assert result['ok'] == ok, result
        return result.get('result') if ok else result

    def lua(code, ok=True):
        return rpc(code=code, ok=ok)

    def until(predicate, timeout=8):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate():
                return
            assert process.poll() is None, 'launcher exited early'
            time.sleep(0.05)
        raise TimeoutError('observable outcome did not arrive')

    def result_path(name):
        return json.dumps((root / (name + '.json')).as_posix(), ensure_ascii=False)

    def result(name):
        path = root / (name + '.json')
        until(path.exists)
        return json.loads(path.read_text(encoding='utf-8'))

    def fixture():
        # LDA $C000; STA $0301; INC $0302; JMP $0900.
        lua('a2.write(0x900,{0xad,0,0xc0,0x8d,1,3,0xee,2,3,0x4c,0,9}); '
            'a2.write(0x302,{0}); a2.set_register("PC",0x900); return true')

    def controller(name):
        return 'r = a2_automation.new({result_path=' + result_path(name) + ',progress_timeout=5}); '

    try:
        until(lambda: (session / 'mailbox/ready.json').exists())
        assert rpc('status')['debugger'] == 'stop'
        assert rpc('status')['driver'] == driver
        rpc('go')
        assert rpc('status')['debugger'] == 'run'
        rpc('pause')
        assert rpc('status')['paused']
        rpc('resume')
        lua('this is malformed Lua )', ok=False)
        lua('error("deliberate runtime error")', ok=False)
        assert 'may have executed' in lua('return function() end', ok=False)['error']
        assert rpc('status')['debugger'] == 'run'  # error did not disable transport
        rpc('pause')
        raw = root / 'marker.bin'
        raw.write_bytes(bytes.fromhex('2c51c02c54c0a9c18d0004a9428d00034c1008'))
        rpc('load_binary', str(raw), 0x800)
        rpc('set_register', 'PC', 0x800)
        marker_bp = rpc('breakpoint', 0x810)['id']
        rpc('go')
        until(lambda: rpc('status')['debugger'] == 'stop')
        assert rpc('read', 0x300, 1)['bytes'] == [66]
        assert rpc('read', 0x400, 1)['bytes'] == [193]
        rpc('clear_breakpoint', marker_bp)
        fixture()
        # Unrelated user breakpoint must survive all controller cleanup.
        unrelated = rpc('breakpoint', 0x1234)['id']
        lua(controller('keys') + '''
            local n=0
            r:phase('fixture', {[0x900]=function(self)
                if n==2 then self:finish(true,'two identical keys consumed'); return end
                if n==0 then
                    local cpu=manager.machine.devices[':maincpu']
                    cpu.state.PC.value=0x903
                    assert(not pcall(function() self:key(13) end))
                    cpu.state.PC.value=0x900
                    cpu.spaces.program:write_u8(0x900,0xea)
                    assert(not pcall(function() self:key(13) end))
                    cpu.spaces.program:write_u8(0x900,0xad)
                end
                self:key(13)
                manager.machine.debugger:command('print b@c000')
                assert(self:pending_key()==13, 'debugger read consumed pending key')
                n=n+1
            end}, function() return true end)
            r:keyboard({0x900})
            assert(not pcall(function() a2.go() end), 'host execution raced controller')
            return true''')
        assert result('keys')['ok']
        assert rpc('read', 0x301, 2)['bytes'] == [141, 2]
        assert lua(f'return manager.machine.devices[":maincpu"].debug:bplist()[{unrelated}] ~= nil')
        capture = rpc('capture', str(root / 'capture'), 0x400, 1024,
                      {'mode': 'text40', 'bank': 'CPU-visible fixture main', 'page': 1})
        assert Path(capture['raw']).stat().st_size == 1024
        assert Path(capture['png']).read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
        fixture()
        unexpected = rpc('breakpoint', 0x903)['id']
        lua(controller('unknown') + '''r:phase('fixture', {[0x900]=function() end}, function() return true end); return true''')
        assert 'unexpected debugger stop' in result('unknown')['reason']
        assert rpc('registers')['PC'] == 0x903
        assert rpc('clear_breakpoint', unexpected)['cleared']
        fixture()
        lua(controller('cancel') + '''r:phase('fixture',{[0x900]=function() end},function() return true end);
            r:keyboard({0x900}); r:key(13); a2.stop_automation('cancelled');
            assert(r:pending_key()==nil); return true''')
        assert result('cancel')['ok'] is False
        lua(controller('bad-detail') + "r:finish(true,'bad adapter detail',function() end); return true")
        assert result('bad-detail')['ok'] is False
        assert result('bad-detail')['receipt_error']
        # Reused PC, new module: only the new handler may run on the next hit.
        fixture()
        lua(controller('overlay') + '''
            local old=0
            r:phase('first',{[0x900]=function(self)
                old=old+1
                self:phase('second',{[0x900]=function(next)
                    assert(old==1); next:finish(true,'new module only')
                end},function() return true end)
            end},function() return true end); return true''')
        assert result('overlay')['ok']
        fixture()
        lua(controller('identity') + """local valid=true
            r:phase('fixture',{[0x900]=function() valid=false end},function() return valid end); return true""")
        assert 'module/bank identity changed' in result('identity')['reason']
        fixture()
        lua('r=a2_automation.new({result_path=' + result_path('watchdog') + ',progress_timeout=1}); ' +
            "r:phase('fixture',{[0x900]=function() manager.machine.devices[':maincpu'].state.PC.value=0x810 end},function() return true end); return true")
        assert 'watchdog expired' in result('watchdog')['reason']
        # Save/load lifecycle invalidates an active controller instead of reusing handles.
        saved = root / 'lifecycle.sta'
        rpc('save', str(saved))
        rpc('go')
        until(lambda: saved.exists() and saved.stat().st_size > 0)
        entry = rpc('breakpoint', 0x810)['id']
        rpc('go')
        until(lambda: rpc('status')['debugger'] == 'stop')
        rpc('clear_breakpoint', entry)
        fixture()
        lua(controller('load') + "r:phase('fixture',{[0x900]=function() end},function() return true end); " +
            'manager.machine:load(' + json.dumps(saved.as_posix()) + "); emu.unpause(); manager.machine.devices[':maincpu'].debug:go(); return true")
        assert result('load')['reason'].startswith('state loaded')
        # Re-enter a verified instruction boundary in the restored loop.
        entry = rpc('breakpoint', 0x810)['id']
        rpc('go')
        until(lambda: rpc('status')['debugger'] == 'stop')
        rpc('clear_breakpoint', entry)
        fixture()
        lua(controller('reset') + '''r:phase('fixture',{[0x900]=function() end},function() return true end);
            manager.machine:soft_reset(); emu.unpause(); manager.machine.devices[':maincpu'].debug:go(); return true''')
        assert result('reset')['reason'].startswith('reset')
        assert not rpc('automation_status')['active']
        # Exit is accepted while stopped/paused; no console stdin wakeup.
        rpc('exit')
        process.wait(timeout=10)
        assert process.returncode == 0
        exit_result = json.loads((session / 'exit.json').read_text(encoding='utf-8'))
        if args.disk:
            assert exit_result['source_unchanged']
            assert hashlib.sha256(args.disk.read_bytes()).hexdigest() == json.loads(
                (session / 'session.json').read_text(encoding='utf-8'))['media']['source_sha256']
        (root / 'smoke.json').write_text(json.dumps({'ok': True, 'receipts': receipts}, indent=2)+'\n', encoding='utf-8')
        bad_startup = root / 'bad-startup.lua'
        bad_startup.write_text('error("deliberate startup failure")', encoding='utf-8')
        failed_session = root / 'failed-session'
        failed_command = command.copy()
        failed_command[failed_command.index('--output-dir')+1] = str(failed_session)
        failed_command[failed_command.index('--timeout')+1] = '2'
        failed_command += ['--startup', str(bad_startup)]
        failed_process = subprocess.Popen(failed_command, stdin=subprocess.DEVNULL)
        try:
            deadline = time.monotonic() + 8
            ready = failed_session / 'mailbox/ready.json'
            while not ready.exists():
                assert time.monotonic() < deadline, 'startup failure receipt absent'
                time.sleep(0.05)
            assert not json.loads(ready.read_text(encoding='utf-8'))['ok']
            try:
                request(failed_session, operation='status')
                raise AssertionError('client accepted failed startup')
            except ValueError as error:
                assert 'startup failed' in str(error)
            pending = failed_session / 'mailbox/request.json'
            pending.write_text('{"id":"must-not-run","code":"return 42"}', encoding='utf-8')
            failed_process.wait(timeout=8)
            assert failed_process.returncode == 124
            assert pending.exists(), 'failed startup executed a request'
            assert not (failed_session / 'mailbox/must-not-run.response.json').exists()
        finally:
            if failed_process.poll() is None:
                failed_process.terminate()
                failed_process.wait(timeout=8)
        print(f'PASS: {driver} mailbox running/pause/stop, errors, two keys, guards, cleanup, overlay, watchdog, reset/load, capture, exit')
        return 0
    finally:
        if process.poll() is None:
            # Ask the owned supervisor to clean up its child before forcing it.
            try:
                request(session, operation='exit', timeout=2)
                process.wait(timeout=8)
            except (OSError, ValueError, subprocess.TimeoutExpired):
                process.terminate()
                process.wait(timeout=8)
        if temporary:
            temporary.cleanup()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (AssertionError, OSError, ValueError, subprocess.SubprocessError) as error:
        import traceback
        traceback.print_exc()
        sys.exit('FAIL: ' + str(error))
