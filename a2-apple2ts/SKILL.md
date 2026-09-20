---
name: a2-apple2ts
description: Control and debug Apple2TS using the configured apple2ts-server MCP, with localhost HTTP as a compatibility option. Use for private sessions, disk and binary uploads, keyboard input, screenshots, CPU and memory inspection, breakpoints, and watchpoints.
---

# A2 Apple2TS

Prefer the already configured `apple2ts-server` MCP. Discover actual tools and
resources; client prefixes may differ. Do not reinstall or reconfigure the server
as part of ordinary emulator work.

## References

- [references/apple2ts-mcp.md](references/apple2ts-mcp.md): primary MCP workflow,
  upload tickets, state resources, tool arguments, and failure handling.
- [references/apple2ts-api.md](references/apple2ts-api.md): selected HTTP sessions
  or capabilities absent from MCP. HTTP may target a different emulator.
- [references/apple2ts-integration.md](references/apple2ts-integration.md): optional
  scratch-session verification with observable results.

## Workflow

1. Inspect MCP session lifecycle; start a private visible/headless session when
   needed and record its identity. Preserve pre-existing sessions.
2. Read machine/execution state and media as relevant. Pause before stable
   CPU/memory setup and observe paused state.
3. Use upload tickets for files, dedicated tools for controls, and bounded
   memory reads. Check tool errors and operation receipts.
4. Verify behavior using execution stops, memory, rendered text, or screenshots.
   Upload completion or keyboard delivery alone does not prove execution.
5. Release held input, remove only owned debugger entries, and stop private
   test sessions created by the task when finished.

Choose reset, boot, and media ejection based on the program's startup needs;
do not eject every disk for every BASIC task. MCP has no direct basic-text tool:
use keyboard entry or a packaged BASIC disk.

For HTTP compatibility, default to `http://127.0.0.1:6502`. The browser needs
remote control and debugging enabled:
`http://127.0.0.1:6502/?remoteControl=1&debug=on`. Do not probe unrelated ports
if unreachable. This browser requirement applies to HTTP; MCP owns its private
browser session.

## Companion routing

- `a2-basic` writes BASIC; `a2-cc65` builds native programs and defines their
  formats/addresses; `a2-a2kit` packages disk images.
- `a2-mame` is an independent Lua-controlled alternative or comparison target.
  Honor explicit emulator choice; use separate sessions and media copies.
- The local `APPLE2TS_REMOTE_CONTROL.md`, if present, is historical project
  evidence, not a universal policy or current MCP specification.
