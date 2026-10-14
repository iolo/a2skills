---
name: a2-mame
description: Control and debug a MAME Apple II emulator remotely through its Lua console or startup scripts. Use for apple2, apple2e, and apple2ee sessions, disk mounting, keyboard input, screenshots, CPU and memory inspection, breakpoints, and comparison with Apple2TS.
---

# A2 MAME

For Windows/macOS setup, shell syntax, and emulator limitations, read
[references/host-platforms.md](references/host-platforms.md) when needed.

Use an owned MAME process with a persistent terminal and `-console`. Read
[references/mame-lua.md](references/mame-lua.md) for launch commands, model
profiles, Lua operations, and verification before controlling a session.

## Workflow

1. Honor an explicit emulator/model choice. Default this skill to `apple2`;
   choose `apple2e` or `apple2ee` explicitly for AppleSoft/IIe workflows.
2. Inspect MAME version, available drivers, ROMs, and media slots. Missing ROMs
   are a prerequisite failure; do not silently substitute a different model.
3. Launch with [scripts/launch.py](scripts/launch.py) in a persistent terminal.
   Use a new output directory and copies of writable media. Load
   [scripts/control.lua](scripts/control.lua) in the console.
4. Inspect `a2.status()` and `a2.devices()`. Pause before stable CPU/memory
   inspection or setup. Mapped memory is not necessarily physical main RAM.
5. Send one command at a time through `a2.call(id, operation, ...)` and wait for
   its matching `A2` receipt. A scheduled-operation receipt is not completion.
6. Verify expected memory, CPU, media, or screen results. Bound host waits;
   never busy-wait in Lua for emulation to advance.
7. Release held inputs and stop only the owned process when finished.

## Alternatives and companions

- `a2-apple2ts` uses the configured Apple2TS MCP and is preferred when no
  emulator is selected and that MCP is available. MAME can run independently
  or alongside it; do not migrate a session silently.
- `a2-gssquared` is a native Apple II/IIgs alternative using a debug socket and
  the upstream Python client or a configured MCP sidecar.
- `a2-basic` and `a2-cc65` write/build programs; `a2-a2kit` packages disk images.
- Compare results on matched models, ROM environments, and media copies.
  Save states and debugger identifiers are emulator-specific.
- Games/graphics guidance belongs to the future `a2-games` skill.
