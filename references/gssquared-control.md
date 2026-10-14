# GSSquared native control

## Control surfaces and prerequisites

Use a configured GSSquared MCP sidecar if available, discovering its actual
tools, arguments, connection lifecycle, and socket target. The upstream MCP
document is a decision record, not a callable schema. The sidecar is external
to the app; do not invent tools or install/reconfigure it for ordinary control.

Otherwise use the upstream **`gs2debug`** Python client. Resolve installed
`gs2debug`, or add an upstream checkout's `clients/python/src` to PYTHONPATH:

```sh
PYTHONPATH=/absolute/gssquared/clients/python/src python3 your_controller.py
```

PowerShell uses `$env:PYTHONPATH = 'C:\src\gssquared\clients\python\src'`
followed by `py -3 your_controller.py`. The smoke script's `--client-src`
argument avoids environment-variable syntax entirely.

The Python package is not bundled with this skill. Prefer it to handwritten
binary framing. There is one client connection per emulator and one outstanding
request at a time. Disconnect an existing controller before switching clients;
do not compete with an attached MCP sidecar. Closing a client leaves the
emulator running. The web build has no native debug socket.

Resolve an explicit executable first, then `GSSquared` on PATH. Linux user
installs commonly use `~/.local/bin/GSSquared` with assets in
`~/.local/share/GSSquared/`. Other releases use a Linux AppImage, macOS
`GSSquared.app/Contents/MacOS/GSSquared`, or Windows portable `GSSquared.exe`.
Native packages bundle ROMs/assets. A standalone copied executable still needs
assets at its build's expected location; diagnose that before changing models.

## Launch and machine selection

Create a new scratch directory and use a unique short AF_UNIX path per instance.
Keep the process/terminal handle. Run emulator and controller in separate
process groups so Ctrl-C in a script cannot interrupt the emulator:

```sh
GSSquared --debug /tmp/owned-gs2/debug.sock -p 3 -s
GSSquared /absolute/copied-machine.gs2 --debug /tmp/owned-gs2/debug.sock
GSSquared -p 3 --debug /tmp/owned-gs2/debug.sock "-ds6d1=/absolute/copied-disk.dsk"
```

The socket directory must exist. Windows also uses a filesystem socket path,
such as `C:\Temp\gs2.sock`, not a TCP port. Bound startup waits; socket-file
existence alone does not prove readiness. Handshake, read platform status, and
observe actual guest execution before CPU setup. The bundled test waits for
instruction trace entries. `no machine` can mean startup or System Select is
pending. Do not remove another process's socket.

The emulator's Windows socket support does not imply that the selected Python
runtime exposes `socket.AF_UNIX`. The smoke script checks transport availability
before launch and reports SKIP (77) if absent. Use a compatible client/runtime
or configured MCP sidecar; see [host platforms](host-platforms.md).

For iterative checks, launch one owned emulator in a persistent terminal or
with `subprocess.Popen(..., start_new_session=True)`, retaining its handle,
socket, log, and copied media. Reconnect successive controllers to that same
socket, with a fresh handshake each time; close each client before the next.
Inspect state on reconnect rather than resetting automatically. Keep the
emulator alive until the task finishes, then perform owned-process cleanup.
This avoids repeating native launch for every checker correction. In sandboxed
hosts, GUI launch or socket access may require escalation. Request it for the
specific launch/controller command when required; session reuse does not
bypass permissions or require a broad arbitrary-Python approval rule.

`start_new_session=True` is POSIX-specific. On Windows the smoke script uses
`creationflags=subprocess.CREATE_NEW_PROCESS_GROUP`. Cleanup targets the
owned process handle on both platforms.

| `-p N` / status ID | Machine |
| --- | --- |
| 0 | Original Apple II |
| 1 | Apple II Plus |
| 2 | Apple IIe |
| 3 | Enhanced Apple IIe; useful default for development |
| 4 | Apple IIe with 65816; VIDHD needs a custom config |
| 5 | Apple IIgs; CLI built-in tile is ROM 01 |

Select IIgs ROM 03 through System Select or an appropriate `.gs2`. ID 5 alone
does not distinguish the ROM. Honor explicit model/ROM choices.

CLI/TOML drives are **1-based**; protocol units are **0-based**:
`-ds6d1=path` corresponds to `mount(6, 0, path)`. A controller must exist in
that slot. CLI mounts override config entries for the same slot/drive.

Configs are TOML with `gs2_version = 1`. Copy an appropriate existing config;
consult the upstream schema for cards, storage, clock, and display keys.
`.gs2` stores configuration and IIgs BRAM, not CPU/RAM execution state.
Load/close may rewrite UUID/BRAM fields. A socket or working directory does
not isolate shared host preferences or `Documents/GSSquared/`. Full machine
save/restore is not shipped in the reviewed source.
Native quit can also write `Documents/gssquared-trace.bin`; the scratch test
isolates its socket/log/media, not all native application output.

## Connect, bounded requests, and events

High-level Python methods normally leave request waits unbounded. Use a
subclass to bound calls while keeping the upstream framing:

```python
from gs2debug import Client, ProtocolError

class BoundedClient(Client):
    def request(self, type_word, payload=b"", *, timeout=5.0):
        return super().request(type_word, payload, timeout=timeout)

with BoundedClient() as c:
    c.connect("/tmp/owned-gs2/debug.sock")
    hello = c.hello()  # required first command; protocol version 1
    status = c.get_status()
    print(hello.version, status.platform_id, status.execution_mode)
    c.ping()
    try:
        print("\n".join(c.video_text().as_lines()))
    except ProtocolError as error:
        if error.code != 6 or error.message != "current mode is not text":
            raise
        print("Guest is in graphics mode; use framebuffer or native capture")
```

After a timeout/framing error, close the connection. Reconnect, handshake, and
inspect state before replaying a mutation with an unknown result.

Run control: `pause()`, `continue_()`, `reset(cold_start=False)`,
`step_into(count=1)`. Cold reset clears `$3F2`–`$3F4`; choose it based on guest
startup needs. Execution modes are 0=NORMAL, 1=STEP_INTO, 2=PAUSED. Mode 1
alone does not prove step completion. STEP replies only arm an instruction
batch; wait for `EVT_STOPPED` / `STOP_STEP`, then inspect live registers.

Explicit `pause()` plus `STOP_PAUSE` yields mode 2. A matching breakpoint
event can instead report mode 1 (the built-in stepping state), including
`STOP_BP_IO` on the tested enhanced IIe. Treat the event's reason/ID as the
stop evidence; do not require mode 2 for every stop. Mode 1 without a matching
event still does not prove that a requested step finished. The
[HGR recipe](gssquared-graphics.md) demonstrates a breakpoint stop and stable
live-register readback.

Register `on_event(handler)` **before** pause/run/step. `request()` dispatches
events received before its reply without retaining them for `wait_stopped()`.
A later wait can miss the stop. Capture stops in a host queue and call
`wait_event(timeout=remaining)` until the queue has the expected reason/ID.
The smoke script demonstrates this with a total deadline. Discard stale
captured stops before new execution; avoid extra queries between run and stop.

Stop reasons: EXEC=1, DATA=2, IO=3, STEP=4, PAUSE=5 (`STOP_*` constants).
The event data begins with little-endian uint32 `reason`, `bp_id`, and full
`pc`, then access metadata and a 40-byte trace snapshot. Read the protocol
for complete layouts. DATA/IO stops occur after the triggering instruction;
their trace fields may describe pre-instruction registers. `get_regs()` gives
the live CPU state.

Breakpoints share the UI table and survive reset. Clear only owned IDs.
CONTINUE steps off an EXEC stop before rearming it (Policy A); step batches
do not check breakpoints. Example definitions on a paused machine:

```python
from gs2debug import BP_KIND_EXEC, BP_KIND_DATA, BP_KIND_IO, BP_ACCESS_W, MEM_MAIN

bp = c.bp_set(kind=BP_KIND_EXEC, address=0x0805)
watch = c.bp_set(kind=BP_KIND_DATA, domain=MEM_MAIN,
                 address=0x0300, access=BP_ACCESS_W)
io = c.bp_set(kind=BP_KIND_IO, address=0xC030, access=BP_ACCESS_W)
# Continue; observe the matching reason/ID; inspect guest results.
for owned_id in (bp, watch, io):
    c.bp_clear(owned_id)
```

IO uses `$C000`–`$C0FF` offsets and a platform bank whitelist. Consult the
client signature/protocol for ranges, temporary flags, ignore counts, address
masks, and byte-value matching. Do not use `bp_clear_all()` for routine cleanup.

## Memory, registers, and programs

| Python domain | Address meaning |
| --- | --- |
| `MEM_MAIN` | Current CPU MMU view; IIgs FPI/banked view |
| `MEM_MEGAII` | IIgs-only Mega II MMU view |
| `MEM_MAIN_RAW` | Physical CPU RAM buffer; IIe aux at `+0x10000` |
| `MEM_MEGAII_RAW` | IIgs-only physical Mega II RAM; aux at `+0x10000` |
| `MEM_ENSONIQ` | IIgs DOC RAM offsets `0..0xFFFF` in current protocol |
| `MEM_ADBMICRO` | Reserved, unsupported |

Mapped reads may touch I/O/soft switches and return floating-bus bytes for
unmapped addresses. Use RAW for passive physical RAM inspection, with bounded
reads (protocol cap 65536 bytes) and writes. Pause/stop for consistent multi-call
snapshots. Verify RAM writes in the same domain. RAW bypasses MMU/video shadow
side effects, so raw writes alone do not establish video or execution mapping.

II/IIe physical text page 1: `MEM_MAIN_RAW, 0x0400`. IIgs text via the CPU MMU:
`MEM_MAIN, 0xE00400`; physical display RAM: `MEM_MEGAII_RAW, 0x0400`.
IIgs `MEM_MAIN_RAW` indexes 8 MB of banks 0–127, not CPU `$E0xxxx` addresses.
MEGAII domains fail on non-IIgs machines. The cookbook's ENSONIQ-unsupported
note is stale relative to the reviewed protocol; check installed capability
before using DOC RAM. Device `state_get()` / `state_set()` blobs are not full
machine checkpoints.

```python
import struct
from pathlib import Path
from gs2debug import MEM_MAIN_RAW, REG_PC

# Paused, with a 40-column main-memory IIe profile:
payload = Path("/absolute/hello.bin").read_bytes()  # raw, not AppleSingle
c.write_mem(MEM_MAIN_RAW, 0x0800, payload)
assert c.read_mem(MEM_MAIN_RAW, 0x0800, len(payload)) == payload
c.set_regs(REG_PC, pc=0x0800)
assert struct.unpack_from("<H", c.get_regs(), 16)[0] == 0x0800
```

`get_regs()` returns a 40-byte binary snapshot. Offsets: PB=15, PC=16, A=18,
X=20, Y=22, SP=24, D=26 (16-bit fields little-endian). `set_regs()` uses a
`REG_*` mask; other fields stay unchanged. GET_REGS omits the 65816 E flag;
SET_REGS can write it. Establish banks/width/emulation mode before executing
a raw 6502 fixture on 65816.

Use linker load/entry/done labels. This repo's raw `hello.bin` starts at `$0800`,
completes at `$0810`, and writes `$0300=$42`, `$0400=$C1`. Loading bytes alone
does not start execution. AppleSingle/runtime binaries and tokenized BASIC
require their proper guest loader and startup environment.

## Input, text, and graphics

At a verified BASIC prompt on a suitable machine, use:

```python
c.paste_text('10 PRINT "GS2 READY"\nRUN\n')
# Let the guest execute and verify output under a deadline.
```

Paste **replaces** the pending buffer; it does not append. The reply precedes
guest consumption; paused guests cannot drain it. Empty paste cancels. Use
ASCII and observe expected output before a second paste; send INPUT answers
after the prompt. An echoed program line does not prove RUN executed.
For graphical applications, wait for a program readiness marker or a known
completed-frame event before injecting keys. HGR/HGR2 can switch modes before
clearing pages or the keyboard strobe; an early key can be discarded by a
later `$C010` access. See the [graphics recipe](gssquared-graphics.md).

`type_text(..., delay_s=0.1)` sends US-layout SDL taps when paste is unsuitable;
faster typing can drop line-number digits. Use `key_down`, `key_up`, and
`tap_key` with constants from `gs2debug.keys` for special/modifier keys. Set
modifier bits on the target event and release held keys in `finally`. Prefer
protocol reset over synthesizing a host-specific Reset shortcut.

`video_text()` provides 40/80-column characters, not bitmap screenshots.
Current-mode selection raises `ProtocolError` code 6, `current mode is not text`,
while the guest is in graphics mode. During a transition, guard/catch that
specific condition or explicitly select page/mode to inspect text RAM; do not
swallow unrelated protocol errors. The graphics reference includes both forms.
`.as_lines()` loses inverse/flashing/alternate-character styling. Forced
page/mode snapshots check RAM, not the visible mode; GS/OS graphics may have
unrelated text RAM. For graphics use native UI capture: File → Save Screenshot
(Shift+PrintScreen) writes PNG to Desktop. There is no documented screenshot
socket method. F4 opens the control panel, F10 the debugger. Speed, display
engine, mouse/gamepad configuration, and dirty-media saves use UI workflows
unless a discovered tool exposes the requested control.

## Media and shutdown

```python
from pathlib import Path
from gs2debug import MEDIA_OK

assert c.mount(6, 0, str(Path("copied-disk.dsk").resolve())) == MEDIA_OK
# Verify guest boot/catalog/output separately.
assert c.unmount(6, 0) == MEDIA_OK  # discards dirty data
```

Check logical media status even when framing succeeded: 0=OK, 1=no drive,
2=mount failed, 3=unmount failed, 4=bad path. Use absolute paths. Disk II/IWM
have units 0–1, BazFast up to 0–5; select slots from the actual config.
Replacing floppy media can discard existing writes. Use copied media in
owned sessions or selected empty drives. Mount success does not prove boot.

Preserve wanted writes through the native save workflow. `unmount()` discards;
`quit()` skips confirmation and dirty-disk prompts. Prefer `c.quit()` for
disposable owned tests and wait for process exit. Harnesses that may need
SIGTERM should launch with `--no-quit-confirm`; otherwise SDL may show a Quit
modal and hang cleanup. Disconnect rather than quitting attached user sessions.

## Optional verification

From the installed skill directory:

```sh
python3 scripts/smoke.py --emulator /absolute/GSSquared \
  --client-src /absolute/gssquared/clients/python/src \
  --platform 3 --output-dir /tmp/new-gs2-iie-test
python3 scripts/smoke.py --emulator /absolute/GSSquared \
  --client-src /absolute/gssquared/clients/python/src \
  --platform 5 --output-dir /tmp/new-gs2-gs-test
```

Omit `--client-src` for installed `gs2debug`. Optional `--disk /absolute/disk.dsk`
checks mount/unmount on a copy; `--slot` / `--unit` default to 6/0. Output
directory must be new. The test verifies handshake, physical memory, register
writes, actual breakpoint/step completion, trace, text RAM, and owned shutdown.
It requires assets and a native display; no headless flag is assumed. It keeps
`emulator.log` and `result.json`. Exit 77 means missing executable/client (SKIP);
runtime failures are FAIL. It does not prove graphical fidelity, MCP, input
behavior, or persistence of dirty media.

## Sources

Reviewed upstream commit `643e6c2107c59cd39182dbb69af600d8833c0505` on 2026-10-06.
Check installed-build differences rather than assuming all releases match.

- [Feature catalog](https://github.com/jawaidbazyar2/gssquared/blob/643e6c2107c59cd39182dbb69af600d8833c0505/Docs/Features.md)
- [Command line](https://github.com/jawaidbazyar2/gssquared/blob/643e6c2107c59cd39182dbb69af600d8833c0505/Docs/CommandLine.md)
- [Python cookbook](https://github.com/jawaidbazyar2/gssquared/blob/643e6c2107c59cd39182dbb69af600d8833c0505/Docs/gs2debug.md)
- [Python client](https://github.com/jawaidbazyar2/gssquared/blob/643e6c2107c59cd39182dbb69af600d8833c0505/clients/python/src/gs2debug/client.py)
- [Debug protocol](https://github.com/jawaidbazyar2/gssquared/blob/643e6c2107c59cd39182dbb69af600d8833c0505/Docs/DebugProtocol.md)
- [MCP decision record](https://github.com/jawaidbazyar2/gssquared/blob/643e6c2107c59cd39182dbb69af600d8833c0505/Docs/McpServer.md)
- [Config schema](https://github.com/jawaidbazyar2/gssquared/blob/643e6c2107c59cd39182dbb69af600d8833c0505/Docs/SystemConfigTOML.md)
