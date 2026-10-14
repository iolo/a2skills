#!/usr/bin/env python3
"""Check or refresh regular-file skill references from canonical references/."""
import argparse
from pathlib import Path
import sys


def sync(root, write=False):
    stale = []
    for path in sorted(root.glob('a2-*/references/*')):
        source = root / 'references' / path.name
        if not source.is_file():
            raise ValueError(f'no canonical reference for {path}')
        expected = source.read_bytes()
        if path.is_symlink() or path.read_bytes() != expected:
            stale.append(path.relative_to(root))
            if write:
                # Unlink first: writing through a legacy symlink would modify
                # the canonical source instead of making a portable copy.
                if path.is_symlink():
                    path.unlink()
                path.write_bytes(expected)
    return stale


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write', action='store_true', help='refresh tracked copies')
    args = parser.parse_args()
    stale = sync(args.root, args.write)
    if stale and not args.write:
        print('FAIL: stale or symlink references; run python scripts/sync_references.py --write')
        for path in stale:
            print(path)
        return 1
    print(f'PASS: references synchronized ({len(stale)} refreshed)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
