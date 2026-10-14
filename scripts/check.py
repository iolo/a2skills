#!/usr/bin/env python3
"""Offline skill/package integrity checks; no external Python dependencies."""
import argparse
import ast
import json
from pathlib import Path
import re
import shutil
import tempfile
from sync_references import sync


def check_skill(skill):
    text = (skill / 'SKILL.md').read_text(encoding='utf-8')
    assert text.startswith('---\n'), f'{skill}: missing frontmatter'
    front = text.split('---', 2)[1]
    assert re.search(r'^name: ' + re.escape(skill.name) + r'$', front, re.M), f'{skill}: name mismatch'
    assert re.search(r'^description: .+', front, re.M), f'{skill}: missing description'
    for path in skill.rglob('*'):
        assert not path.is_symlink(), f'non-portable symlink: {path}'
        if not path.is_file():
            continue
        if path.suffix == '.json':
            json.loads(path.read_text(encoding='utf-8'))
        if path.suffix == '.py':
            ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        if path.suffix == '.md':
            content = path.read_text(encoding='utf-8')
            assert not re.fullmatch(r'\.\./\.\./references/[^\r\n]+\s*', content), f'symlink placeholder: {path}'
            for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
                if re.match(r'[a-z]+:', target) or target.startswith('#'):
                    continue
                target = target.split('#')[0]
                assert (path.parent / target).exists(), f'{path}: missing {target}'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = p.parse_args()
    skills = sorted(args.root.glob('a2-*/SKILL.md'))
    assert skills, 'no skills found'
    assert not sync(args.root), 'stale references; run python scripts/sync_references.py --write'
    with tempfile.TemporaryDirectory(prefix='a2-installed-') as temporary:
        for entry in skills:
            check_skill(entry.parent)
            installed = Path(temporary) / entry.parent.name
            shutil.copytree(entry.parent, installed, symlinks=False,
                            ignore=shutil.ignore_patterns('__pycache__'))
            check_skill(installed)
    for path in (args.root / 'references').glob('*.json'):
        json.loads(path.read_text(encoding='utf-8'))
    print(f'PASS: {len(skills)} skill metadata, local links, JSON, Python syntax, materialized packages')


if __name__ == '__main__':
    main()
