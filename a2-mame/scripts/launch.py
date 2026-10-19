#!/usr/bin/env python3
"""Launch and supervise an owned Apple II MAME session with isolated artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import os
import shutil
import signal
import subprocess
import sys
import time


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mame', default='mame')
    p.add_argument('--driver', choices=('apple2', 'apple2e', 'apple2ee'))
    p.add_argument('--profile', choices=('floppy', 'iie-cffa'), default='floppy')
    p.add_argument('--rompath', type=Path, required=True)
    p.add_argument('--cffa-rom', type=Path, help='local cffa20ee02.bin (6502 firmware) for iie-cffa')
    p.add_argument('--pluginspath', type=Path, help='MAME plugins directory containing console and json')
    p.add_argument('--output-dir', type=Path, required=True, help='new private session directory')
    p.add_argument('--disk', type=Path, help='copied to flop1, or hard1 for iie-cffa')
    p.add_argument('--transport', choices=('console', 'mailbox'), default='console')
    p.add_argument('--script', type=Path, help='legacy autoboot Lua (runs after emulation starts)')
    p.add_argument('--startup', type=Path, help='mailbox initialization Lua; runs even at initial debugger stop')
    p.add_argument('--debug', action='store_true')
    p.add_argument('--debugger', help='backend, e.g. qt, windows, osx; implies --debug')
    display = p.add_mutually_exclusive_group()
    display.add_argument('--headless', action='store_true', help='SDL dummy drivers, no video/audio')
    display.add_argument('--visible', action='store_true', help='show video/audio (default)')
    speed = p.add_mutually_exclusive_group()
    speed.add_argument('--throttle', action='store_true', help='original speed (default)')
    speed.add_argument('--fast', action='store_true', help='disable throttle, independent of visibility')
    p.add_argument('--read-config', action='store_true', help='opt into installed MAME configuration')
    p.add_argument('--bgfx-chain', help='opt-in visible BGFX screen chain')
    p.add_argument('--avi', help='opt-in AVI filename inside this session')
    p.add_argument('--timeout', type=float, help='overall monotonic host deadline in seconds')
    args = p.parse_args()
    if args.timeout is not None and not 0 < args.timeout < float('inf'):
        p.error('--timeout must be finite and positive')
    if args.startup and (args.transport != 'mailbox' or args.script):
        p.error('--startup requires mailbox and cannot be combined with --script')
    if args.cffa_rom and args.profile != 'iie-cffa':
        p.error('--cffa-rom requires --profile iie-cffa')
    if args.profile == 'iie-cffa' and args.driver not in (None, 'apple2e'):
        p.error('iie-cffa uses unenhanced apple2e; do not silently change models')
    if args.headless and args.bgfx_chain:
        p.error('--bgfx-chain requires visible output')
    if args.avi and (Path(args.avi).name != args.avi or args.avi in ('.', '..')):
        p.error('--avi must be a filename inside the session')
    driver = args.driver or ('apple2e' if args.profile == 'iie-cffa' else 'apple2')
    executable = shutil.which(args.mame)
    if not executable:
        p.error('MAME unavailable; supply --mame /path/to/mame')
    executable = str(Path(executable).resolve())
    candidates = [args.pluginspath] if args.pluginspath else [
        Path(executable).parent / 'plugins',
        Path(executable).parent.parent / 'share/mame/plugins',
        Path('/opt/homebrew/share/mame/plugins'), Path('/usr/local/share/mame/plugins'),
        Path('/usr/share/games/mame/plugins'), Path('/usr/share/mame/plugins')]
    plugins = next((path.resolve() for path in candidates if path and
                    all((path / plugin / 'init.lua').is_file() for plugin in ('console', 'json'))), None)
    if plugins is None:
        p.error('console/json plugins not found; supply --pluginspath /path/to/mame/plugins')
    rompath = args.rompath.resolve()
    if not rompath.is_dir():
        p.error('ROM directory does not exist')
    for path in (args.disk, args.script, args.startup, args.cffa_rom):
        if path is not None and not path.is_file():
            p.error(f'file not found: {path}')
    out = args.output_dir.resolve()
    out.mkdir(mode=0o700, parents=True, exist_ok=False)
    rompaths = str(rompath)
    if args.cffa_rom:
        card = out / 'roms/a2cffa02'
        card.mkdir(parents=True)
        shutil.copyfile(args.cffa_rom, card / 'cffa20ee02.bin')
        rompaths = str(out / 'roms') + ';' + rompaths
    hardware = ['-aux', 'ext80', '-ramsize', '64K', '-sl7', 'cffa202'] if args.profile == 'iie-cffa' else []
    for target in ([driver, 'a2cffa02'] if hardware else [driver]):
        subprocess.run([executable, target, '-noreadconfig', '-rompath', rompaths,
                        '-verifyroms'], check=True, timeout=30)
    scripts = Path(__file__).resolve().parent
    pluginpaths = str(plugins)
    if args.transport == 'mailbox':
        pluginpaths = (scripts / 'plugins').as_posix() + ';' + pluginpaths
        (out / 'mailbox').mkdir(mode=0o700)
    command = [executable, driver, '-readconfig' if args.read_config else '-noreadconfig',
               '-rompath', rompaths, *hardware, '-pluginspath', pluginpaths,
               '-skip_gameinfo', '-window', '-nomouse', '-homepath', str(out),
               '-nothrottle' if args.fast else '-throttle']
    command += ['-console'] if args.transport == 'console' else ['-noconsole', '-plugins', '-plugin', 'a2_mailbox']
    for option in ('cfg_directory', 'nvram_directory', 'snapshot_directory', 'state_directory', 'diff_directory'):
        directory = out / option
        directory.mkdir()
        command.extend(['-' + option, str(directory)])
    media = None
    if args.disk:
        source = args.disk.resolve()
        disk = out / ('media.hdv' if hardware else 'media' + source.suffix)
        before = digest(source)
        shutil.copyfile(source, disk)
        assert digest(disk) == before == digest(source), 'media changed while copying'
        media = {'source': str(source), 'copy': str(disk), 'source_sha256': before}
        command.extend(['-hard1' if hardware else '-flop1', str(disk)])
    if args.script:
        command.extend(['-autoboot_script', str(args.script.resolve()), '-autoboot_delay', '0'])
    if args.debug or args.debugger or args.transport == 'mailbox':
        command.append('-debug')
        backend = args.debugger or ('qt' if args.headless else None)
        if backend:
            command.extend(['-debugger', backend])
    env = os.environ.copy()
    for key in ('A2_MAME_SESSION', 'A2_MAME_SCRIPTS', 'A2_MAME_STARTUP'):
        env.pop(key, None)
    if args.transport == 'mailbox':
        env.update(A2_MAME_SESSION=out.as_posix(), A2_MAME_SCRIPTS=scripts.as_posix())
        if args.startup:
            env['A2_MAME_STARTUP'] = args.startup.resolve().as_posix()
    if args.headless:
        env.update(SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', QT_QPA_PLATFORM='offscreen')
        command.extend(['-video', 'none', '-sound', 'none'])
    if args.bgfx_chain:
        command.extend(['-video', 'bgfx', '-bgfx_screen_chains', args.bgfx_chain])
    if args.avi:
        command.extend(['-aviwrite', str(out / args.avi)])
    # MAME paths use semicolon-separated search roots on every supported host.
    hashes = {str(path): digest(path) for path in scripts.rglob('*')
              if path.is_file() and path.suffix in ('.lua', '.json', '.py')}
    for path in (args.startup, args.script, args.cffa_rom):
        if path:
            hashes[str(path.resolve())] = digest(path)
    manifest = {'command': command, 'driver': driver, 'profile': args.profile,
                'transport': args.transport, 'media': media, 'sha256': hashes}
    write_json(out / 'session.json', manifest)
    print('Session: ' + str(out), flush=True)
    log = None
    if args.transport == 'console':
        helper = (scripts / 'control.lua').as_posix()
        print('Load helpers: a2 = dofile(' + json.dumps(helper, ensure_ascii=False) + ')', flush=True)
    else:
        log = (out / 'mame.log').open('wb')
    started = time.monotonic()
    reason = 'exited'
    def interrupted(signum, frame):
        raise KeyboardInterrupt
    previous_sigterm = signal.signal(signal.SIGTERM, interrupted)
    process = None
    try:
        process = subprocess.Popen(command, env=env, cwd=out,
                                   stdin=subprocess.DEVNULL if log else None,
                                   stdout=log, stderr=log)
        manifest['pid'] = process.pid
        write_json(out / 'session.json', manifest)
        try:
            code = process.wait(timeout=args.timeout) if args.timeout else process.wait()
        except (KeyboardInterrupt, subprocess.TimeoutExpired) as error:
            reason = 'timeout' if isinstance(error, subprocess.TimeoutExpired) else 'interrupted'
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
            code = 124 if reason == 'timeout' else 130
        result = {'returncode': code, 'reason': reason, 'host_seconds': time.monotonic() - started}
        if media:
            result.update(source_unchanged=digest(Path(media['source'])) == media['source_sha256'],
                          copy_sha256=digest(Path(media['copy'])))
        write_json(out / 'exit.json', result)
        return code
    finally:
        # Also clean up if writing a manifest or another host-side operation fails.
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        signal.signal(signal.SIGTERM, previous_sigterm)
        if log:
            log.close()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, subprocess.SubprocessError) as error:
        sys.exit(str(error))
