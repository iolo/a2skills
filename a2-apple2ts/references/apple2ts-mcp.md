# Apple2TS server MCP

## Discovery and identity

Checked against configured `apple2ts-server` revision
`8f4cd0df38a142dbfe4212f815cff5f094715bc2`. Live tool schemas take precedence.
Names below omit client-specific prefixes such as `mcp__apple2ts__`.
Discover resources before reading their URIs.

| Resource | Purpose |
| --- | --- |
| `apple2ts://session/lifecycle` | Ownership and lifecycle of the private session |
| `apple2ts://machine` | Machine configuration |
| `apple2ts://session/execution` | Worker-confirmed state and execution sequence |
| `apple2ts://cpu` | Registers; pause for stable observations |
| `apple2ts://debugger/breakpoints` | Existing breakpoints to preserve |
| `apple2ts://disks/current` | Mounted media |
| `apple2ts://system/softswitches` | Memory/video mapping |
| `apple2ts://video/text` | Rendered text for assertions |

Check MCP `isError`. Successful results generally contain `emulator` plus
`state` or `value`; upload preparation returns `ticket`. These are not HTTP
`{ok,data}` envelopes. Record `serverInstanceId`, `rendererId`, and `targetId`
and reject observations from an unexpected session.

## Session and control tools

- `start_session({visibility:"headless"})` or `"visible"`; omission uses the
  configured default. Inspect lifecycle first and preserve pre-existing work.
- `pause({})`, `resume({})`, `boot({})`, `reset({})`, `stop_session({})`.
  Boot/reset are changes, not connection checks.
- `set_speed({speed:0})` accepts integers -2 through 4.
- `capture_screen({})` returns image content and dimensions/MIME metadata.
- `set_cpu({PC:2048})` accepts one or more of PC, A, X, Y, S, PStatus. PC is
  0–65535, other registers 0–255. Pause and verify after changes.

This revision has no MCP save-state, model-selection, single-step, or direct
BASIC mount tools. Do not invent equivalents. HTTP operations require a
separately identified compatible HTTP session.

## Upload workflow

1. Resolve a regular, non-symlink file to an absolute path and determine its
   format. AppleSingle is not a raw memory block.
2. Ensure the uploader can run (including any host permission checks) before
   requesting the short-lived ticket. Call `prepare_mount_disk({path,driveId,expectedSha256})` for fd1/fd2/hd1/hd2,
   or `prepare_load_binary({path,address,expectedSha256})` for raw bytes.
   SHA-256 is optional. Limits: floppy 2 MiB, hard-drive image 32 MiB.
3. Immediately pass the ticket as exactly one line to `apple2ts-upload` stdin,
   then close stdin. Use a subprocess input argument, not shell interpolation.
   Keep ticket URLs out of committed logs.
4. Resolve the uploader from an explicit path, then PATH. If absent, inspect
   the configured MCP launcher's installation directory and package `bin`
   declaration. This server supplies `node <server-root>/cli/apple2ts-upload.mjs`.
   Do not install another server or assume a repository-specific absolute path.
5. Check exit status and receipt identity, byte count/hash, and destination.
   Loading does not start execution. Read memory or media state afterward.

Tickets expire quickly. Inspect completion before preparing another ticket;
transport failure does not establish that no effects occurred.

## Keyboard

`send_keys({keys:"RUN\r",timeoutMs:2000})` accepts 1–32 discrete keys. The
emulator must be running and software must clear its keyboard strobe. Split
long BASIC listings into bounded chunks, continuing only after `completed`.
Inspect `keysDelivered`, `keyMayHaveBeenObserved`, and `outcome`: completed,
timeout, interrupted, not_running, or input_busy. Never replay partially
delivered commands automatically. The deadline is not key duration.

`set_keyboard_key({key:"A",repeat:false})` holds a key; release with
`set_keyboard_key({key:null})` during cleanup. Avoid mixing held and queued input.

## Memory and debugger

- `read_memory({address,length,space:"main"})`: use small ranges; active means
  CPU-mapped, main/aux mean physical reads. Pause for physical reads. `auxBank`
  selects an auxiliary bank where supported. Inspect effective mapping metadata.
- `find_memory({address,length,bytes:[...],maxMatches:16,space:"main"})` searches
  a bounded paused range without returning the scanned contents.
- `write_memory({address,bytes:[...]})` writes at most 256 bytes in the current
  CPU mapping, without implicit pause or verification. I/O `$C000–$CFFF` can
  trigger side effects. Failures may leave partial writes; read back RAM changes.
- `set_breakpoint({address})` creates a pausing address breakpoint;
  `clear_breakpoint({address})` removes an owned entry. Avoid clearing all
  breakpoints when unrelated debugger state exists.
- `set_memory_write_watchpoint({address,length,space:"main"})` requires pause
  and does not resume. Save its returned executionSequence. There is one
  session write watchpoint; preserve unrelated use.
- `wait_for_execution_stop({timeoutMs:2000,afterSequence,expectedBreakpointAddress})`
  waits without changing execution. `expectedBreakpointId` is also supported.
  Use a sequence captured before resume to distinguish a new stop. Inspect
  outcome, expectationMatched, pauseReason, and breakpoint/memoryWrite details.
  Timeout does not pause; session_closed is not a successful stop.
- `clear_memory_write_watchpoint({})` requires pause.

Stop on identity changes or contradictory state and report the last confirmed
observation; do not try speculative reset/remount recovery.
