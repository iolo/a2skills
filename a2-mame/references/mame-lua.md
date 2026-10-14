# MAME Apple II Lua control

## Prerequisites and launch

Baseline: MAME 0.285, Python 3, MAME console/json plugins, and locally supplied
ROMs. Inspect `mame -help`, `mame -listfull 'apple2*'`, and
`mame apple2 -listmedia`. Verify a selected profile with
`mame apple2 -rompath /absolute/roms -verifyroms`.

| Driver | Intended use |
| --- | --- |
| `apple2` | Default original Apple II / Integer BASIC ROM; raw 6502 fixture |
| `apple2e` | Unenhanced IIe, AppleSoft and DOS/ProDOS development |
| `apple2ee` | Enhanced IIe, closest profile to Apple2TS `APPLE2EE` |

Driver availability does not prove ROM availability. Do not substitute a model
when its ROMs are missing. C fixtures use AppleSoft ROM routines; they are not
bare original-Apple-II examples. For original Apple II C support, see cc65's
`apple2-integer-basic-compat.o` option and separately verify the runtime setup.

From the installed skill directory, start a persistent terminal:

```sh
python3 scripts/launch.py --driver apple2 --rompath /absolute/roms \
  --output-dir ./build/new-mame-session --debug
```

Optional flags: `--mame /path/to/mame`, `--pluginspath /path/to/mame/plugins`,
`--disk /path/to/demo.dsk`, `--headless`, `--script /path/to/startup.lua`,
`--debugger qt` (or another backend provided by the installed build).
The directory must be new. The launcher copies the disk, isolates writable
configuration/state/screenshot paths, ignores existing machine config, and
executes MAME without a shell. It never fetches ROMs. Headless uses SDL dummy
drivers and no video/audio output; screenshots still use the emulated screen.
Visible `--debug` sessions use MAME's platform default debugger unless
`--debugger` is supplied. Headless debugging defaults to Qt and sets
QT_QPA_PLATFORM=offscreen. The Qt backend must be compiled into MAME for the
full smoke test. Do not select the `none` backend: in 0.285 it resumes
immediately at each stop, so Lua cannot reliably inspect a breakpoint.

For PowerShell, use `py -3` and a single-line command with quoted paths.
Plugin discovery covers adjacent plugins, common Homebrew prefixes, and Linux
package paths; supply `--pluginspath` for other layouts. Native Windows launch
keeps a waitable parent process. The full automated smoke test still requires
a POSIX PTY and skips Windows. See [host platforms](host-platforms.md).

Keep the returned terminal/process handle. Send Lua over that same terminal;
this is local process control, not a network server or attachment to a random
already-running MAME. The launcher prints the absolute helper path:

```lua
a2 = dofile('/absolute/a2-mame/scripts/control.lua')
a2.call('inspect-1', 'status')
a2.call('devices-1', 'devices')
```

Wait for `A2 {"id":...,"ok":...}` with the matching id. Ignore terminal echo,
ANSI controls, and unrelated MAME logs. Send commands sequentially. A helper
error gives `ok:false`; inspect it before continuing. Use a host deadline
(normally 5 seconds per command), never a Lua busy loop. Save/restore/reset/go
receipts mean scheduled, not completed: observe subsequent state or artifacts.

## Operations

The table shows helper calls; wrap them with `a2.call(id, name, arguments...)`
when machine-readable receipts are useful. Memory/CPU operations require a
pause or debugger stop.

| Helper | Meaning |
| --- | --- |
| `status()`, `devices()` | Version, model, pause/debug state; CPU/image/screen tags |
| `pause()`, `resume()` | Ordinary pause; resume refuses a debugger stop |
| `reset()` | Schedule soft reset; re-inspect machine and media |
| `registers(tag)` | Actual register names and values (6502 uses SP, not MCP S) |
| `set_register(name,value,tag)` | Set PC/A/X/Y/SP/P and return registers |
| `read(address,length,tag)` | 1–4096 CPU-mapped bytes; no physical main/aux promise |
| `write(address,bytes,tag)` | Bounded write with read-back; partial effects possible on failure |
| `load_binary(path,address,tag)` | Load 1–4096 raw bytes, verify, leave PC unchanged |
| `keys(text)` | Queue up to 256 bytes through natural keyboard; use `\r` for Return |
| `mount(imageTag,path)`, `eject(imageTag)` | Use discovered image tags, not invented fd1 names |
| `screenshot(path,screenTag)` | Write PNG; single-screen default, otherwise explicit tag |
| `save(path)`, `restore(path)` | Schedule MAME save-state operation |
| `breakpoint(address,cpuTag)` | Return owned breakpoint id; requires --debug |
| `clear_breakpoint(id,cpuTag)` | Remove that breakpoint only |
| `go(cpuTag)`, `step(cpuTag)` | Debugger run/one-instruction step; observe resulting stop |
| `exit()` | Schedule owned session shutdown |

CPU defaults to `:maincpu` after validating its program space; inspect devices
before using it for another configuration. MAME's SP includes stack page one:
use $0100–$01FF, unlike Apple2TS's byte-sized S. Helpers reacquire objects after
reset rather than retaining stale device handles. On IIe, mapped memory follows
soft switches: these reads are not Apple2TS physical main/aux reads. The helper
refuses `$C000–$CFFF` to avoid accidental I/O. Explicit hardware experiments can
use the native Lua address-space API after identifying the intended side effect.
Do not use direct-pointer reads as a general substitute for mapped reads.

MAME 0.285 requires explicit condition/action strings for reliable Lua `bpset`:
the helper supplies `'1', ''`. Omitting them crashed the tested build. Distinguish
`machine.paused` from `machine.debugger.execution_state == 'stop'`.

Natural-keyboard queuing does not prove consumption; verify text/memory/screen.
For held physical inputs, enumerate `machine.ioport.ports` and each port's fields,
then use that field's `set_value` / `clear_value`. Record and clear every field
you change. Keyboard matrix fields and joystick/paddle mappings differ by driver;
do not transplant Apple2TS key codes or assume universal joystick fields.

## Raw fixture walkthrough

Build `hello.bin` with the cc65 skill. It has entry `$0800` and done `$0810`.
In a scratch 40-column main-memory profile:

```lua
a2.call('pause-1', 'pause')
a2.call('load-1', 'load_binary', '/absolute/hello.bin', 0x0800)
a2.call('pc-1', 'set_register', 'PC', 0x0800)
a2.call('bp-1', 'breakpoint', 0x0810)
a2.call('run-1', 'go')
```

After returning to the host, poll `status` with a bounded deadline. At debugger
stop, expect PC `$0810`, `read(0x0300,1)` = 66 and `read(0x0400,1)` = 193.
Capture a screenshot after a rendered frame. Remove the returned breakpoint
id, not all breakpoints. C AppleSingle files must be packaged and BRUN from DOS
or BASIC.SYSTEM, not passed to `load_binary`.

For BASIC, mount a copied bootable DEMOBAS disk, verify the prompt, queue
`RUN DEMOBAS\r`, then `CODEX\r` after the NAME prompt, and observe HELLO CODEX.
The original `apple2` ROM is not an AppleSoft environment; use a verified IIe
profile or explicitly load the required interpreter.

## Optional verification and side-by-side use

Run `python3 scripts/smoke.py --rompath /absolute/roms --driver apple2` from the
skill directory. It launches a scratch process, checks Lua receipts, raw loading,
memory, breakpoints, stepping, screenshots, and cleanup (including waking the console read with a newline after exit). Missing prerequisites
report SKIP with exit 77; assertion/runtime failures are FAIL. Repeat with
apple2e/apple2ee where ROMs are available.

For saves, wait for a nonempty state file, change a scratch RAM marker, restore,
allow the scheduled load to finish, pause, and verify the original marker.
Use only the same MAME version, driver, ROMs, and media configuration. No
save-state interchange with Apple2TS is promised.

For comparisons, run separate copied media on MAME apple2ee and Apple2TS
APPLE2EE with matching 40-column/main-memory assumptions. Compare output text,
completion bytes, and control flow, not exact pixels, wall time, or save states.
Stop on failed assertions; preserve logs and terminate only owned processes.

## Sources

- [MAME Lua entry points](https://docs.mamedev.org/luascript/index.html)
- [Core/session API](https://docs.mamedev.org/luascript/ref-core.html)
- [Memory API](https://docs.mamedev.org/luascript/ref-mem.html)
- [Input API](https://docs.mamedev.org/luascript/ref-input.html)
- [Debugger API](https://docs.mamedev.org/luascript/ref-debugger.html)
- [0.285 debugger bindings](https://github.com/mamedev/mame/blob/mame0285/src/frontend/mame/luaengine_debug.cpp)

The online manuals can describe a newer MAME than installed; verify version
and runtime capabilities. The source link pins the tested breakpoint binding.
