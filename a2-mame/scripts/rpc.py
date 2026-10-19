#!/usr/bin/env python3
"""Issue one request to an owned local MAME mailbox; never auto-retry mutations."""
import argparse
import json
import os
from pathlib import Path
import sys
import time
import uuid


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def request(session, *, operation=None, args=None, code=None, timeout=10):
    if (operation is None) == (code is None):
        raise ValueError('supply exactly one of operation or code')
    if not 0 < timeout <= 60 or (args is not None and not isinstance(args, list)):
        raise ValueError('timeout must be in (0,60]; args must be a list')
    directory = Path(session) / 'mailbox'
    if not directory.is_dir():
        raise ValueError('Session has no mailbox')
    deadline = time.monotonic() + timeout

    def healthy():
        for name in ('transport-error.json', 'protocol-error.json'):
            if (directory / name).exists():
                raise ValueError(f'Terminal mailbox failure: {read_json(directory / name)}')

    ready = directory / 'ready.json'
    while not ready.exists():
        healthy()
        if time.monotonic() >= deadline:
            raise TimeoutError('MAME mailbox did not become ready')
        time.sleep(0.05)
    healthy()
    if not read_json(ready).get('ok'):
        raise ValueError(f'Mailbox startup failed: {read_json(ready)}')
    identifier = uuid.uuid4().hex
    value = {'id': identifier}
    if operation is not None:
        value.update(operation=operation, args=[] if args is None else args)
    else:
        value['code'] = code
    pending, lock = directory / 'request.json', directory / 'client.lock'
    try:
        handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise ValueError('Another mailbox client owns this session; do not remove a live lock') from error
    try:
        with os.fdopen(handle, 'w', encoding='utf-8') as output:
            json.dump({'pid': os.getpid(), 'id': identifier}, output)
        if pending.exists():
            raise ValueError('An earlier request is pending; inspect it before sending another')
        for path in directory.glob('*.request.json'):
            if not path.with_name(path.name.replace('.request.json', '.response.json')).exists():
                raise ValueError(f'An accepted request has no receipt yet: {path.name}')
        temporary = directory / f'{identifier}.tmp'
        with temporary.open('x', encoding='utf-8') as output:
            json.dump(value, output, ensure_ascii=False)
        os.replace(temporary, pending)
        response_path = directory / f'{identifier}.response.json'
        while not response_path.exists():
            healthy()
            if time.monotonic() >= deadline:
                raise TimeoutError(f'No receipt for {identifier}; inspect request/receipt before retrying a mutation')
            time.sleep(0.05)
        response = read_json(response_path)
        if response.get('id') != identifier:
            raise ValueError('Mismatched mailbox receipt')
        return response
    finally:
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session', type=Path, required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--call', dest='operation', help='a2 helper operation')
    action.add_argument('--lua', dest='code', help='local Lua code returning a JSON-compatible value')
    parser.add_argument('--args', default='[]', help='JSON positional argument array')
    parser.add_argument('--timeout', type=float, default=10)
    options = parser.parse_args()
    try:
        response = request(options.session, operation=options.operation, code=options.code,
                           args=json.loads(options.args), timeout=options.timeout)
        print(json.dumps(response, ensure_ascii=False))
        return 0 if response.get('ok') else 1
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
