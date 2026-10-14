#!/usr/bin/env python3
"""Copy a DOS/ProDOS base image, import one program, and verify its payload."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile


def resolve_tool(explicit=None):
    """Use only a bundle matching the host OS/architecture, then search PATH."""
    import platform
    if explicit:
        return shutil.which(explicit)
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch = {'amd64': 'x86_64', 'aarch64': 'arm64'}.get(machine, machine)
    assets = Path(__file__).resolve().parents[1] / 'assets'
    filename = 'a2kit.exe' if system == 'windows' else 'a2kit'
    # New bundles can cover Intel Macs and ARM hosts without ambiguous names.
    candidates = [assets / 'tools' / f'{system}-{arch}' / filename]
    legacy = {('linux', 'x86_64'): 'a2kit', ('darwin', 'arm64'): 'a2kit-mac',
              ('windows', 'x86_64'): 'a2kit.exe'}.get((system, arch))
    if legacy:
        candidates.append(assets / legacy)
    for candidate in candidates:
        found = shutil.which(str(candidate))
        if found:
            return found
    return shutil.which('a2kit')


def applesingle(data):
    if len(data) < 26 or struct.unpack_from('>II', data) != (0x00051600, 0x00020000):
        raise ValueError('expected an AppleSingle v2 file')
    count = struct.unpack_from('>H', data, 24)[0]
    entries = {}
    if 26 + count * 12 > len(data):
        raise ValueError('truncated AppleSingle directory')
    for i in range(count):
        kind, offset, length = struct.unpack_from('>III', data, 26 + i * 12)
        if offset < 26 + count * 12 or offset + length > len(data) or kind in entries:
            raise ValueError('invalid AppleSingle entry')
        entries[kind] = data[offset:offset + length]
    if not entries.get(1) or len(entries.get(11, b'')) != 8:
        raise ValueError('AppleSingle needs data and ProDOS information entries')
    _, filetype, address = struct.unpack('>HHI', entries[11])
    if filetype != 6 or address > 65535:
        raise ValueError('this recipe accepts AppleSingle BIN files only')
    return entries[1], address


def main():
    # Redirected stdout on Windows may otherwise use a legacy code page.
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--format', choices=('basic', 'raw', 'applesingle'), required=True)
    p.add_argument('--address', type=lambda s: int(s, 0), help='required for raw; decimal or 0xHEX')
    p.add_argument('--base-image', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True, help='new directory; must not exist')
    p.add_argument('--name', required=True, help='new root filename, uppercase, 1–15 characters')
    p.add_argument('--a2kit', help='explicit executable; otherwise compatible bundled tool, then PATH')
    args = p.parse_args()
    if not re.fullmatch(r'[A-Z][A-Z0-9.]{0,14}', args.name):
        p.error('name must start with A–Z and contain only A–Z, 0–9, or dot (max 15)')
    if (args.format == 'raw') != (args.address is not None):
        p.error('--address is required only for raw input')
    tool = resolve_tool(args.a2kit)
    if not tool:
        p.error('a2kit unavailable; supply --a2kit /path/to/a2kit')
    tool = str(Path(tool).resolve())

    def run(*words, data=None):
        return subprocess.run([tool, *map(str, words)], input=data, capture_output=True,
                              check=True, timeout=60).stdout

    source = args.source.read_bytes()
    if not source:
        p.error('source is empty')
    address = args.address
    if args.format == 'basic':
        address = 2049
        payload = run('tokenize', '-t', 'atxt', '-a', address, data=source)
        kind = 'atok'
    elif args.format == 'applesingle':
        payload, address = applesingle(source)
        kind = 'bin'
    else:
        payload, kind = source, 'bin'
    if not 0 <= address <= 65535 or address + len(payload) > 65536:
        p.error('program does not fit the 16-bit address space')
    base = args.base_image.resolve()
    before = hashlib.sha256(base.read_bytes()).hexdigest()
    stat = json.loads(run('stat', '-d', base))
    if stat['fs_name'] not in ('a2 dos', 'prodos'):
        p.error('base image must contain DOS 3.3 or ProDOS')
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=False)
    # Never publish a partially verified disk image.
    with tempfile.TemporaryDirectory(dir=out) as scratch:
        disk = Path(scratch) / ('program' + base.suffix)
        shutil.copyfile(base, disk)
        tree = json.loads(run('tree', '-d', disk))
        if args.name in tree.get('files', {}):
            raise ValueError(f'{args.name} already exists in base image')
        run('put', '-d', disk, '-f', args.name, '-t', kind, '-a', address, data=payload)
        extracted = run('get', '-d', disk, '-f', args.name, '-t', kind)
        if extracted != payload:
            raise ValueError('extracted program differs from imported payload')
        metadata = json.loads(run('get', '-d', disk, '-f', args.name, '-t', 'any'))
        if stat['fs_name'] == 'prodos':
            expected_type = 0xFC if kind == 'atok' else 6
            if int(metadata['fs_type'], 16) != expected_type or int.from_bytes(bytes.fromhex(metadata['aux']), 'little') != address:
                raise ValueError('ProDOS file type/load address mismatch')
        else:
            if int(metadata['fs_type'], 16) != (2 if kind == 'atok' else 4):
                raise ValueError('DOS file type mismatch')
            if kind == 'bin':
                header = bytes.fromhex(metadata['chunks']['0'])[:4]
                if struct.unpack('<HH', header) != (address, len(payload)):
                    raise ValueError('DOS binary address/length header mismatch')
        catalog = run('catalog', '-d', disk).decode()
        if hashlib.sha256(base.read_bytes()).hexdigest() != before:
            raise ValueError('base image changed during packaging')
        (out / 'catalog.txt').write_text(catalog, encoding='utf-8')
        (out / 'file-metadata.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
        (out / 'payload.bin').write_bytes(payload)
        if kind == 'atok':
            (out / 'listing.bas').write_bytes(run('detokenize', '-t', 'atok', data=extracted))
        result = {'disk': disk.name, 'name': args.name, 'format': args.format,
                  'address': address, 'bytes': len(payload), 'filesystem': stat['fs_name'],
                  'base_sha256': before, 'payload_sha256': hashlib.sha256(payload).hexdigest()}
        shutil.move(str(disk), out / disk.name)
        (out / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(out / 'manifest.json')


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as error:
        sys.exit(error.stderr.decode(errors='replace').strip() or str(error))
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        sys.exit(str(error))
