#!/usr/bin/env python3
"""Launch an owned Apple II MAME Lua console with isolated output paths."""
import argparse
from pathlib import Path
import os
import shutil
import subprocess
import sys


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mame', default='mame')
    p.add_argument('--driver', choices=('apple2', 'apple2e', 'apple2ee'), default='apple2')
    p.add_argument('--rompath', type=Path, required=True)
    p.add_argument('--pluginspath', type=Path, help='MAME plugins directory containing console and json')
    p.add_argument('--output-dir', type=Path, required=True, help='new session directory')
    p.add_argument('--disk', type=Path, help='copied before use in flop1')
    p.add_argument('--script', type=Path, help='optional startup Lua script')
    p.add_argument('--debug', action='store_true')
    p.add_argument('--headless', action='store_true', help='SDL dummy drivers, no video/audio output')
    args = p.parse_args()
    executable = shutil.which(args.mame)
    if not executable:
        p.error('MAME unavailable; supply --mame /path/to/mame')
    executable = str(Path(executable).resolve())
    candidates = [args.pluginspath] if args.pluginspath else [
        Path(executable).parent / 'plugins', Path('/usr/share/games/mame/plugins'),
        Path('/usr/share/mame/plugins')]
    plugins = next((path.resolve() for path in candidates if path and (path / 'console/init.lua').is_file()), None)
    if plugins is None:
        p.error('console plugin not found; supply --pluginspath /path/to/mame/plugins')
    rompath = args.rompath.resolve()
    if not rompath.is_dir():
        p.error('ROM directory does not exist')
    for path in (args.disk, args.script):
        if path is not None and not path.is_file():
            p.error(f'file not found: {path}')
    subprocess.run([executable, args.driver, '-noreadconfig', '-rompath', str(rompath),
                    '-verifyroms'], check=True, timeout=30)
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    command = [executable, args.driver, '-noreadconfig', '-rompath', str(rompath),
               '-console', '-pluginspath', str(plugins), '-skip_gameinfo', '-window', '-nomouse', '-homepath', str(out)]
    for option in ('cfg_directory', 'nvram_directory', 'snapshot_directory', 'state_directory', 'diff_directory'):
        directory = out / option
        directory.mkdir()
        command.extend(['-' + option, str(directory)])
    if args.disk:
        disk = out / ('media' + args.disk.suffix)
        shutil.copyfile(args.disk, disk)
        command.extend(['-flop1', str(disk)])
    if args.script:
        command.extend(['-autoboot_script', str(args.script.resolve()), '-autoboot_delay', '0'])
    if args.debug:
        command.extend(['-debug', '-debugger', 'qt'])
    env = os.environ.copy()
    if args.headless:
        env.update(SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', QT_QPA_PLATFORM='offscreen')
        command.extend(['-video', 'none', '-sound', 'none'])
    print('Load helpers: a2 = dofile(' + repr(str(Path(__file__).with_name('control.lua').resolve())) + ')', flush=True)
    os.chdir(out)
    os.execve(executable, command, env)


if __name__ == '__main__':
    try:
        main()
    except (OSError, subprocess.SubprocessError) as error:
        sys.exit(str(error))
