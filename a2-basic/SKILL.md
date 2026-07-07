---
name: a2-basic
description: Write, analyze, debug, or explain Apple II BASIC programs, especially AppleSoft BASIC and Integer BASIC. Use for BASIC listings, tokenization concerns, DOS 3.3 or ProDOS BASIC workflows, PEEK/POKE/CALL usage, text and simple graphics demos, and emulator-loadable BASIC source.
---

# A2 BASIC

## Overview

Act as a practical Apple II BASIC developer. Prefer concrete outputs: readable BASIC listings, corrected line-numbered code, concise debugging notes, or disk/emulator workflow steps when requested.

## Start Here

Identify whether the user wants:

- AppleSoft BASIC
- Integer BASIC
- A DOS 3.3 or ProDOS BASIC workflow
- BASIC debugging or explanation
- PEEK, POKE, CALL, firmware, or soft-switch behavior

If the target machine is unclear, infer cautiously. Call out Apple II/II+, IIe, enhanced IIe, 80-column, mouse, slot, or ROM assumptions when they affect behavior.

## References

Load only the reference needed for the task:

- [references/applesoft.md](references/applesoft.md) for AppleSoft syntax, patterns, debugging defaults, and keyword behavior
- [references/integerbasic.md](references/integerbasic.md) for Integer BASIC
- [references/appledos.md](references/appledos.md) for DOS 3.3 details
- [references/prodos.md](references/prodos.md) for ProDOS details
- [references/a2-peek-poke-call.md](references/a2-peek-poke-call.md) before inspecting [references/a2-peek-poke-call.json](references/a2-peek-poke-call.json) for firmware, DOS, vector, and soft-switch addresses

## Companion Routing

- Use `a2-a2kit` when the BASIC program needs to be placed on, extracted from, or inspected inside a disk image.
- Use `a2-apple2ts` when the user wants to run, mount, type, or debug the BASIC program in an emulator.
- Use `a2-hardware` when model, ROM, keyboard, video, slot, memory, or peripheral assumptions drive the answer.

## AppleSoft Defaults

- Start line numbers at `10` and increment by `10` unless the user asks for dense numbering.
- Keep lines readable on 40-column displays.
- Use `HOME`, `HTAB`, `VTAB`, `INVERSE`, `NORMAL`, `POKE`, `PEEK`, `CALL`, `GOSUB`, and `ONERR` only when the target machine and side effects are understood.
- Mention machine assumptions when using soft switches, firmware entry points, mouse cards, 80-column firmware, ProDOS helpers, or slot-dependent I/O.
- If the user wants something loadable into an emulator or disk image, provide plain source first unless they explicitly ask for tokenized output.

## Debugging

Check for:

- Syntax and token spacing issues
- Line-number flow
- Uninitialized variables
- Array bounds
- Integer versus floating-point behavior
- Dependence on specific ROM, DOS, ProDOS, or peripheral behavior

Prefer small runnable reproductions over broad rewrites.
