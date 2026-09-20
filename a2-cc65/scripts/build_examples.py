#!/usr/bin/env python3
"""Build installed skill fixtures without writing beside their sources."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'assets/examples')
    p.add_argument('--output-dir', type=Path, required=True, help='new directory; must not exist')
    for tool in ('cl65', 'ca65', 'ld65'):
        p.add_argument('--' + tool, default=tool)
    args = p.parse_args()
    tools = {}
    for tool in ('cl65', 'ca65', 'ld65'):
        found = shutil.which(getattr(args, tool))
        if not found:
            p.error(f'{tool} unavailable; supply --{tool} /path/to/{tool}')
        tools[tool] = str(Path(found).resolve())
    source = args.source_dir.resolve()
    for name in ('hello.c', 'mixed.c', 'twice.s', 'hello.s', 'raw.cfg'):
        if not (source / name).is_file():
            p.error(f'missing source: {source / name}')
    out = args.output_dir.resolve()
    if out == source or source in out.parents:
        p.error('output directory must be outside the source directory')
    out.mkdir(parents=True, exist_ok=False)
    shutil.copytree(source, out / 'src')

    def run(tool, *words):
        subprocess.run([tools[tool], *words], cwd=out, check=True, timeout=60)

    run('cl65', '-t', 'apple2', '-m', 'hello.map', '-o', 'hello.as', 'src/hello.c')
    run('cl65', '-t', 'apple2', '-m', 'mixed.map', '-o', 'mixed.as', 'src/mixed.c', 'src/twice.s')
    run('ca65', '-o', 'hello.o', 'src/hello.s')
    run('ld65', '-C', 'src/raw.cfg', '-m', 'raw.map', '-Ln', 'raw.lbl', '-o', 'hello.bin', 'hello.o')
    manifest = {
        'hello.as': {'format': 'applesingle', 'expected': 'APPLE II C READY', 'requires': 'AppleSoft ROM, DOS 3.3 or ProDOS BASIC.SYSTEM'},
        'mixed.as': {'format': 'applesingle', 'expected': 'MIXED RESULT: 42', 'requires': 'AppleSoft ROM, DOS 3.3 or ProDOS BASIC.SYSTEM'},
        'hello.bin': {'format': 'raw', 'load_address': 2048, 'entry_address': 2048,
                      'expected_memory': {'0x0300': 66, '0x0400': 193},
                      'requires': '6502, main-memory 40-column Apple II text'},
    }
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(out / 'manifest.json')


if __name__ == '__main__':
    try:
        main()
    except (OSError, subprocess.SubprocessError) as error:
        sys.exit(str(error))
