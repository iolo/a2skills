---
name: a2-cc65
description: Write, build, analyze, or debug Apple II native programs with the cc65 toolchain, including cc65 C, ca65 6502 assembly, cl65 builds, mixed C/assembly projects, raw binary loaders, firmware calls, soft switches, text-page drawing, zero-page usage, and direct hardware access.
---

# A2 cc65

## Overview

Act as a practical Apple II native-code developer using the `cc65` toolchain: `cc65`, `ca65`, `ld65`, and `cl65`. Prefer concrete outputs: C source, `ca65` source, `cl65` build commands, linker notes, memory maps, debugger checks, and concise explanations of instruction or hardware behavior.

## Start Here

Identify whether the user wants:

- Apple II C with `cc65` / `cl65`
- 6502 assembly with `ca65`
- mixed C/assembly
- custom linker or segment behavior
- raw binary loading
- direct firmware, soft-switch, or hardware access

If the target machine is unclear, infer cautiously. State Apple II/II+, IIe, enhanced IIe, ROM, DOS/ProDOS, slot, and peripheral assumptions when they affect runtime behavior.

## References

Load only the reference needed for the task:

- [references/cc65.md](references/cc65.md) for `cc65`, `ca65`, `ld65`, and `cl65` build patterns
- [references/6502.md](references/6502.md) for 6502 instruction behavior, addressing modes, and `ca65` patterns
- [references/6502-opcodes.md](references/6502-opcodes.md) before inspecting [references/6502-opcodes.json](references/6502-opcodes.json) for exact opcode bytes or cycle counts
- [references/hardware-and-firmware.md](references/hardware-and-firmware.md) for Apple II model and firmware details
- [references/a2-peek-poke-call.md](references/a2-peek-poke-call.md) before inspecting [references/a2-peek-poke-call.json](references/a2-peek-poke-call.json) for firmware, DOS, vector, and soft-switch addresses

## Companion Routing

- Use `a2-a2kit` when a built program needs to be packaged into, extracted from, or verified inside a disk image.
- Use `a2-apple2ts` when the user wants to run, mount, load, or debug the built program in an emulator.
- Use `a2-hardware` when model, ROM, slot, soft-switch, memory, display, or peripheral assumptions drive the answer.

## Defaults

- Prefer `cl65 -t apple2` for simple one-file C or assembly programs.
- Use `ca65` plus `ld65` when custom segments, linker config, or object-level control matters.
- Use labels instead of hard-coded branch offsets.
- Separate zero-page, code, data, and string areas clearly.
- Keep C memory use modest and avoid assuming large heap availability.
- Use small, fixed buffers in C.
- Drop to assembly for hot loops, firmware hooks, or hardware register access that is awkward in C.
- Comment non-obvious hardware accesses or firmware entry points.
- State expected load address, machine family, and DOS/ProDOS assumptions.

## C Guidance

- Confirm whether console, file I/O, joystick support, or runtime behavior exists for the selected target.
- Document addresses, ROM calls, or soft switches when C code talks directly to Apple II hardware.
- Keep mixed C/assembly interfaces small and explicit: document calling convention, clobbered registers, zero-page use, and memory ownership.

## Assembly Guidance

- Prefer zero page for hot paths, but make zero-page ownership explicit.
- Remember that displayed text bytes usually need the high bit set.
- Keep board/state memory separate from screen scratch memory.
- Be careful with shared zero-page scratch variables across nested drawing helpers.
- If flicker matters, draw static UI once and redraw only changed regions.

## Raw Binary Workflow

When output is a raw Apple II binary from `cl65 -t apple2 -C apple2-asm.cfg` or equivalent:

1. Prefer emulator `binary-block` mounting over debugger memory writes for normal loading.
2. Use the produced binary name as `filename`.
3. Use the known load address, commonly `$0803` / `2051` for `apple2-asm.cfg`.
4. Use debugger memory writes only for precise inspection, patching, or when the mount path is insufficient.

When a program works in memory but not on screen, verify runtime state, game buffers, and screen memory separately before assuming rendering tells the whole story.
