# Event-driven automation, input, and capture

## Adapter and controller boundaries

Load `scripts/automation.lua` as `a2_automation` in a console, or use the mailbox's
preloaded global. At a verified debugger stop, create one controller with
`a2_automation.new{result_path='/absolute/new-result.json', progress_timeout=180}`.
Retain it in a global such as `player`. Choose a fresh result path for each run.
The helper owns only its returned breakpoint IDs and its optional keyboard tap;
it never clears all breakpoints. Terminal completion/failure pauses execution,
removes those resources, clears pending input, and writes a structured result.
A `finish(true, reason, detail)` is an adapter assertion, not an emulator inference.

Install `player:phase(name, handlers, guard)`, where handlers maps each PC to a
prompt callback and guard is a required function confirming loaded module and
bank identity. The guard is checked before installation and at every stop.
A callback must return promptly; do not loop waiting for emulated execution.
The periodic dispatcher checks `machine.debugger.execution_state == 'stop'`,
checks consumption of the previous key, calls the matching handler under `pcall`,
and resumes using `emu.unpause()` then `cpu.debug:go()`. Unknown PCs or guard
failures produce diagnostic results and remain paused. The lookup is by PC;
it cannot distinguish two stop reasons at the same owned PC. Avoid overlapping
manual watch/breakpoints there during automation.

Typical adapter outline (symbols and predicates must be supplied by the program):

```lua
player = a2_automation.new {
    result_path = os.getenv('A2_MAME_SESSION') .. '/result.json',
    progress_timeout = 180
}
player:phase('gameplay', {
    [symbols.POLL_KEY] = function(self)
        if finished_in_native_state() then
            self:finish(true, 'terminal input wait', native_state())
            return
        end
        self:key(next_menu_key())
    end
}, verify_module_and_banks)
player:keyboard({symbols.POLL_KEY})
```

Install the first phase at a stop included in its handlers (often a boot/entry
handler which needs no input). To transition overlays, remove the old phase's
handlers at its handoff, install a load/entry phase, then verify the new module
before installing its polling handlers. `phase` clears only owned IDs and resets
the allowed keyboard sites. Use build-produced symbol maps and fingerprints;
a PC value alone is insufficient when intro/game overlays reuse addresses.
Never use a guard returning `true` outside a controlled scratch fixture.

Only one controller may be active. The `a2` mutating/execution helpers reject
independent host commands until `a2.stop_automation(reason)` is called. Read-only
inspection still requires a stable stop. Arbitrary native Lua can bypass this
contract; coordinate it explicitly. `a2.automation_status()` exposes active state
and the final result. Stopping the controller keeps MAME alive. Creating another
controller reacquires CPU/space handles; completed callbacks remain inert.

The helper invalidates and cleans up on reset, state load, or machine stop; it
never resumes an adapter with stale handles or symbols. Stop before requesting
reset/load through `a2`. Native/UI reset/load is a failure boundary, not automatic
recovery. Re-observe state and reconstruct the adapter after that lifecycle event.
The progress watchdog uses coarse host `os.time()`; `launch.py --timeout` separately
bounds total monotonic host time, including a stuck Lua callback. Do not equate
host sleeps with emulated time under throttle/fast-forward.

## Choose an input mode

| Mode | Use | Observe |
| --- | --- | --- |
| Natural keyboard (`a2.keys`) | Strings and ordinary program interaction | Queue delivery **and** program consumption |
| Physical fields | Arrows, modifiers, joystick/driver input testing | Enumerated field, press, emulated release interval |
| One-shot response (`player:key`) | Instrumented polling at known instructions | Exactly one real read and the expected native action |

A posted Return can survive a debugger stop and affect the following menu.
`a2.keyboard_status()` exposes `empty`, `is_posting`, and emulated time. Wait for
both empty and not posting plus an adapter-chosen emulated idle interval, then
verify the intended menu/text change. Empty queue alone does not prove consumption.
Repeated physical arrows need a release interval in emulated time. Modifiers
may also confirm menus. Enumerate the chosen driver's fields; retain/release all
fields you set. Temporary taps that suppress stale keys/buttons during draining
are instrumented workarounds, not evidence for unmodified physical input.

The opt-in one-shot adapter requires `player:keyboard({poll_pc, ...})` in the
current phase. `player:key(byte)` accepts 7-bit bytes only when stopped at one of
those PCs and after checking CPU-visible instruction bytes `AD 00 C0` (`LDA $C000`).
It rejects a wrong PC/opcode or an already pending key. The retained read tap
substitutes `byte | 0x80` on the next read with side effects enabled, then clears
the byte. A debugger read with side effects disabled cannot consume it; the next
handler asserts it was consumed. Do not call native `space:read_u8(0xC000)` to
check delivery: that API can have side effects even while stopped. Use
`player:pending_key()` to inspect the pending byte without reading hardware.

This is one response, not full latch/typematic/modifier emulation. Its correctness
depends on resuming directly into the verified instruction; it does not identify
the caller intrinsically. Short opcode checks do not prove binary identity.
Programs which reread the latch need their own adapter. Key meanings are
consumer-specific (even cursor codes); keep them outside the generic helper.

## Completion and persistence

Define terminal predicates for every relevant input handler. An outcome may
reach a different polling routine from normal gameplay; otherwise automation
can press through the completed screen and report a later error. Require an
explicit result with the native state. A familiar prompt, one counter, or MAME
exit code zero is not enough.

Check three levels where relevant: the intended input/menu choice, native program
completion, and persisted contents after clean exit. Continue saved progress in a
fresh process when testing persistence. This is distinct from a program's saved
case restore and from MAME save-state compatibility. Keep route/trait/score logic
and program-specific addresses in an adapter rather than this skill.

## Capture without losing the state

A screenshot taken at a debugger stop can contain the previous rendered frame.
`a2.capture(prefix, address, length, mapping, screenTag)` saves `.png`, raw `.bin`,
and `.json` metadata without advancing emulation. It accepts up to 16K below
mapped I/O and requires a mapping table with `mode`, `page`, and `bank`; include
actual relevant soft-switch values too. The helper reads the current CPU mapping,
not guaranteed physical main RAM, and records status/registers and possible pixel
lag. It does not infer display mode, bank, or render raw data.

For a known standard HGR mapping, an adapter can observe PAGE2 (`$C01C`) and dump
8,192 bytes at `$2000` or `$4000`, then render that offline. This does not generalize
to double-hires, 80-column text, or arbitrary IIe banks. Record ALTZP/RAMRD/RAMWRT
and display switches when needed; mapped zero page can be auxiliary. Avoid
substituting direct-pointer reads without understanding the mapping. If advancing
one rendered frame instead, first establish that it cannot lose the target state.

The no-PTY smoke exercises repeated identical keys, debugger reads, rejection of
wrong PC/opcode, unknown stops, owned cleanup, reused PCs, watchdogs, and reset/load invalidation.
Full program adapters, bank-switch transitions, and load recovery need their own
integration evidence. Current upstream APIs: [debugger](https://docs.mamedev.org/luascript/ref-debugger.html),
[memory](https://docs.mamedev.org/luascript/ref-mem.html), and
[core/session](https://docs.mamedev.org/luascript/ref-core.html). Online docs may
be newer than the tested MAME 0.285 runtime.
