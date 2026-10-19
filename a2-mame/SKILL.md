---
name: a2-mame
description: Control and debug owned MAME Apple II sessions through a Lua console or local file mailbox. Use for apple2, apple2e, and apple2ee disk/binary loading, keyboard input, screenshots, CPU/memory inspection, and breakpoint-driven automation.
---

# A2 MAME

Use an owned MAME process. Choose **console** for interactive Lua in a persistent
terminal, or **mailbox** for automation without stdin, including debugger stops.
Read [Lua control](references/mame-lua.md) for the helper API and console workflow;
read [mailbox and profiles](references/mame-mailbox.md) for unattended sessions.
For host setup or Windows/macOS differences, read
[host platforms](references/host-platforms.md).

## Workflow

1. Honor the requested model. Default to `apple2`; choose `apple2e`/`apple2ee`
   explicitly for IIe workflows. Inspect MAME version, ROMs, and configured
   media slots. Missing ROMs are a prerequisite failure, not a reason to switch.
2. Launch [scripts/launch.py](scripts/launch.py) with a new private output
   directory and copied writable media. Select transport and profile explicitly
   when defaults do not fit. Visibility and throttle are independent.
3. Inspect `a2.status()` and `a2.devices()`. Pause for stable inspection; use a
   verified debugger stop for instruction-boundary changes. CPU-mapped memory
   may be auxiliary RAM; record relevant mapping switches.
4. Issue one command and match its receipt. `scheduled` means accepted, not
   completed. After a timeout, inspect the exact request and receipt before
   retrying a mutation. Startup failure is terminal for that mailbox session.
5. For repeated decisions, use [event-driven automation](references/mame-automation.md).
   Give execution to one controller. Keep symbols, module/bank checks, input
   semantics, and terminal predicates in a separate program adapter.
6. Verify program outcomes and saved contents, not just counters or process exit.
   Capture raw bytes and mapping metadata when paused pixels may lag. Bound host
   waits; never wait inside a Lua callback for the CPU to advance.
7. Stop automation, release held input, and exit only the owned process. Wait for
   exit before inspecting saved media; inspect result receipts and source hashes.

## Companions and verification

- `a2-apple2ts` is preferred when no emulator is selected and its MCP is available;
  do not silently migrate a selected MAME session. `a2-gssquared` is another native
  Apple II/IIgs option.
- `a2-basic` and `a2-cc65` build programs; `a2-a2kit` packages disks.
- Compare matched models, ROMs, and copied media. Save states and debugger IDs
  are emulator-specific.
- [scripts/smoke.py](scripts/smoke.py) preserves the POSIX console regression;
  [scripts/smoke_mailbox.py](scripts/smoke_mailbox.py) exercises the mailbox and
  automation without a PTY. Both need local ROMs. Report PASS/FAIL/SKIP separately;
  Linux MAME 0.285 evidence does not establish other versions/hosts as supported.
