# apple2ts API

Use this reference when the user wants to control or inspect an `apple2ts` emulator over HTTP.

Source of truth:

- GitHub OpenAPI spec: `https://github.com/ct6502/apple2ts/blob/main/server/openapi.json`
- Fetched during skill creation from the raw spec at `https://raw.githubusercontent.com/ct6502/apple2ts/main/server/openapi.json`

## Operating assumptions

- The server is localhost-only.
- The OpenAPI spec declares server URL `/`, so use the local host and port exposed by the running `apple2ts` instance.
- Read state first when the port or current machine configuration is unknown.

## Core endpoints

### Machine control

- `GET /api/machine`: Read current machine state
- `PATCH /api/machine`: Update machine configuration
- `POST /api/machine/boot`: Boot emulator
- `POST /api/machine/reset`: Reset emulator
- `POST /api/machine/pause`: Pause execution
- `POST /api/machine/resume`: Resume execution

Important `MachinePatch` fields:

- `runMode`: `running` or `paused`
- `speedMode`: integer
- `machineName`: `APPLE2EU` or `APPLE2EE`
- `ramWorksKb`: `64`, `512`, `1024`, `4096`, `8192`
- `debugEnabled`: boolean
- `showDebugPanel`: boolean

Example:

```sh
curl -s http://127.0.0.1:6502/api/machine
curl -s -X PATCH http://127.0.0.1:6502/api/machine \
  -H 'Content-Type: application/json' \
  -d '{"machineName":"APPLE2EE","debugEnabled":true}'
curl -s -X POST http://127.0.0.1:6502/api/machine/reset
```

### Keyboard and mouse input

- `POST /api/input/keys`
- `POST /api/input/apple-keys`
- `POST /api/input/mouse`

`KeyInputRequest` accepts three shapes:

- `{ "type": "key", "key": "A", "release": true }`
- `{ "type": "keyCode", "keyCode": 13, "release": true }`
- `{ "type": "text", "text": "PRINT CHR$(4);\"CATALOG\"\r" }`

`AppleKeyRequest`:

- `side`: `left` or `right`
- `pressed`: boolean

`MouseInputRequest`:

- `x`: integer
- `y`: integer
- `buttons`: integer bitmask/value

Examples:

```sh
curl -s -X POST http://127.0.0.1:6502/api/input/keys \
  -H 'Content-Type: application/json' \
  -d '{"type":"text","text":"RUN\r"}'

curl -s -X POST http://127.0.0.1:6502/api/input/keys \
  -H 'Content-Type: application/json' \
  -d '{"type":"key","key":"RETURN","release":true}'

curl -s -X POST http://127.0.0.1:6502/api/input/apple-keys \
  -H 'Content-Type: application/json' \
  -d '{"side":"left","pressed":true}'
```

Use text injection for whole commands. Use key or keyCode payloads when timing, modifiers, or exact keyboard semantics matter.

### Drive and media control

- `GET /api/drives`
- `GET /api/drives/{driveId}`
- `PATCH /api/drives/{driveId}`
- `DELETE /api/drives/{driveId}` to eject media
- `POST /api/drives/{driveId}/mount`

Drive ids:

- `fd1`
- `fd2`
- `hd1`
- `hd2`

`DrivePatch`:

- `writeProtected`: boolean

`MountMediaRequest` fields:

- `sourceType`: one of `base64`, `url`, `library-id`, `binary-block`, `basic-text`
- `filename`: optional filename hint
- `dataBase64`: for base64 media payloads
- `url`: for remote media source
- `libraryId`: for library-backed media
- `address`: integer load address for `binary-block`
- `autoRun`: boolean
- `text`: for `basic-text`

Examples:

```sh
curl -s http://127.0.0.1:6502/api/drives

curl -s -X POST http://127.0.0.1:6502/api/drives/fd1/mount \
  -H 'Content-Type: application/json' \
  -d '{"sourceType":"url","url":"http://example.local/demo.dsk","filename":"demo.dsk"}'

curl -s -X POST http://127.0.0.1:6502/api/drives/fd1/mount \
  -H 'Content-Type: application/json' \
  -d '{"sourceType":"basic-text","filename":"hello.bas","text":"10 PRINT \"HELLO\"\n20 END\n","autoRun":true}'
```

Use `basic-text` when the user wants a quick BASIC program mounted directly. Use `binary-block` only when you know the correct load address.

### Debugging and memory

- `GET /api/debug/cpu`
- `PATCH /api/debug/cpu`
- `GET /api/debug/memory?start=...&length=...&format=bytes|hex`
- `PUT /api/debug/memory`
- `GET /api/debug/memory/full`
- `GET /api/debug/soft-switches`
- `POST /api/debug/soft-switches`
- `POST /api/debug/step-into`
- `POST /api/debug/step-over`
- `POST /api/debug/step-out`
- `GET /api/debug/breakpoints`
- `POST /api/debug/breakpoints`
- `PATCH /api/debug/breakpoints/{breakpointId}`
- `DELETE /api/debug/breakpoints/{breakpointId}`
- `DELETE /api/debug/breakpoints`

Useful request shapes:

- `MemoryWriteRequest`: `{ "start": 768, "data": [169, 0, 96] }`
- `SoftSwitchWriteRequest`: `{ "addresses": [49246, 49247] }`
- `BreakpointCreate`: at minimum `{ "address": 49152 }`

Examples:

```sh
curl -s 'http://127.0.0.1:6502/api/debug/memory?start=768&length=32&format=hex'

curl -s -X PUT http://127.0.0.1:6502/api/debug/memory \
  -H 'Content-Type: application/json' \
  -d '{"start":768,"data":[169,66,141,0,4,96]}'

curl -s -X POST http://127.0.0.1:6502/api/debug/breakpoints \
  -H 'Content-Type: application/json' \
  -d '{"address":1024}'
```

Always re-read CPU or memory state after mutating it. Prefer snapshots or save-state export before large debugger sessions.

### Snapshots and save states

- `GET /api/debug/snapshots`
- `POST /api/debug/snapshots`
- `POST /api/debug/snapshots/{snapshotId}/activate`
- `POST /api/debug/snapshots/step-back`
- `POST /api/debug/snapshots/step-forward`
- `POST /api/save-states/export`
- `POST /api/save-states/import`

Payloads:

- `SaveStateExportRequest`: optional `{ "includeSnapshots": true }`
- `SaveStateImportRequest`: `{ "dataBase64": "..." }`

Example:

```sh
curl -s -X POST http://127.0.0.1:6502/api/save-states/export \
  -H 'Content-Type: application/json' \
  -d '{"includeSnapshots":true}'
```

## Response shape

Most success responses are envelopes like:

```json
{ "ok": true, "data": { ... } }
```

Handle errors explicitly instead of assuming an empty body means success.

## Practical guidance

- Use `GET /api/machine` and `GET /api/drives` first in exploratory sessions.
- Use `POST /api/machine/pause` before low-level debugger changes.
- Use `POST /api/machine/resume` only after confirming CPU and memory state.
- Use snapshots for stepping experiments and save-state export for longer checkpoints.
- Prefer explicit JSON payloads over ad hoc shell escaping when sending BASIC text with quotes or carriage returns.
