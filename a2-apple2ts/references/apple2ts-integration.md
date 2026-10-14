# Optional Apple2TS integration checks

Use a private scratch session. Record PASS, FAIL, or SKIP per scenario with
server revision, model, and observed results. See [apple2ts-mcp.md](apple2ts-mcp.md).

## Raw execution and debugging

1. Build the cc65 skill's `hello.bin`. Its manifest and `raw.lbl` give entry
   `$0800` and `done` `$0810`; do not assume these addresses for other programs.
2. Start a private session, pause, upload at 2048, and compare 19 bytes against
   the file. Record execution sequence.
3. Set PC=2048 and a breakpoint at 2064, resume, and wait at most 2 seconds for
   that stop. Expect PC=2064, main `$0300=$42`, and main `$0400=$C1`.
4. Capture the screen. CPU execution may stop before a rendered frame; memory
   is the primary assertion, not immediate pixel appearance.
5. Clear the owned breakpoint, set PC=2048, arm a main-memory write watchpoint
   at 768 length 1, resume, and wait after its returned sequence. Expect a write
   of 66 at 768, writer PC `$080D`, and a watchpoint stop.
6. Clear the watchpoint while paused. Resume the final loop and perform a short
   bounded stop wait; expect timeout. Pause again.

## Disk, BASIC, and input

1. Package the BASIC fixture as DEMOBAS on a copied bootable disk. Mount through
   a ticket, read the drives resource, and boot the scratch session.
2. Observe the OS prompt. For ProDOS, launch BASIC.SYSTEM if needed. Send
   `RUN DEMOBAS\r` and confirm APPLE II BASIC READY and NAME in the text resource.
3. Send `CODEX\r`; confirm HELLO CODEX and capture the screen.
4. Run packaged C/mixed fixtures with `BRUN DEMOC` / `BRUN DEMOMIX`, check their
   expected text, and send the exit key. Use a fresh packaged image per recipe.
5. While paused, verify keyboard delivery reports not_running rather than
   silently starting execution. Eject only test media.

Always release held input, remove owned debugger entries, and stop the private
session in cleanup, including after failures. Confirm closed lifecycle.
Save-state operations are unsupported by this MCP revision; do not import
HTTP state from a different session. Historical project-specific HTTP failures
are not evidence about current MCP behavior.
