---
name: a2-apple2ts
description: Control, inspect, debug, or automate an apple2ts emulator over its localhost HTTP API. Use for machine state, drives, mounting media, keyboard input, reset/boot, memory/CPU/debugger operations, breakpoints, save states, screenshots, and running BASIC or binary-block programs.
---

# A2 Apple2TS

## Overview

Act as a careful operator of a local `apple2ts` emulator. Read the API reference before sending emulator requests and verify state before and after important mutations.

## Reference

Read [references/apple2ts-api.md](references/apple2ts-api.md) before sending API requests. Treat it as authoritative; do not guess endpoint names.

## Defaults

Unless the user explicitly requests a different host or port, use:

```text
http://127.0.0.1:6502
```

Do not probe random localhost ports. If that server does not respond, tell the user `apple2ts` is not reachable, suggest starting the local server, and ask for a different port only if their setup does not use `6502`.

## Workflow

1. Confirm the local server is reachable.
2. Start exploratory sessions with `GET /api/machine`.
3. Use `GET /api/drives` only when drive or media state matters.
4. Read machine state before mutating it.
5. Use the smallest API call that solves the problem.
6. Re-read state after boot, reset, mount, memory writes, CPU changes, breakpoint changes, or save-state restore.
7. Prefer save-state export or snapshots before invasive debugging when reversibility matters.

When automating text entry, prefer `/api/input/keys` with `type: "text"` for whole strings and `type: "key"` or `type: "keyCode"` for precise keypresses.

When mounting media, be explicit about drive ids: `fd1`, `fd2`, `hd1`, or `hd2`.

To run an AppleSoft BASIC program, unmount all media to avoid boot priority, restart and reset for clean state, then mount the BASIC file.

For raw assembly binaries, prefer `sourceType: "binary-block"` with a known load address and `autoRun: true` over debugger memory writes unless precision patching is required.

## Companion Routing

- Use `a2-basic` when the task is to write, fix, or explain the BASIC program before running it.
- Use `a2-cc65` when build commands, load addresses, binary format, C/assembly source, or native-code debugging decisions are needed.
- Use `a2-a2kit` when media must be inspected, created, converted, or modified before mounting.
