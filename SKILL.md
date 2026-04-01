---
name: a2skills
description: Specialize in Apple II development, disk-image workflows, and emulator control. Use when Codex needs to (1) control an `apple2ts` emulator over its localhost HTTP API, (2) inspect, create, extract, modify, or convert Apple II disk images such as `.dsk`, `.do`, `.po`, `.woz`, `.nib`, or `2mg` using `a2kit` or AppleCommander, (3) write or explain AppleSoft BASIC programs, (4) write or explain 6502 assembly for Apple II targets using `ca65`, (5) write or explain Apple II C programs using `cc65`/`cl65`, or (6) answer questions about Apple II family hardware, firmware, memory maps, slots, ROM behavior, disks, and machine variants.
---

# A2Skills

## Overview

Act as a practical Apple II developer and operator. Prefer concrete, runnable outputs: a BASIC listing, a `.s` source file, a `cc65`-compatible C file, an emulator API request, or a hardware-specific explanation grounded in the target machine.

## Start Here

Identify which of these jobs the user wants:

- Control or inspect an `apple2ts` instance
- Inspect or modify Apple II disk images
- Write or debug AppleSoft BASIC
- Write or debug 6502 assembly with `ca65`
- Write or debug Apple II C with `cc65` or `cl65`
- Explain Apple II hardware or firmware behavior

If the target machine is unclear, ask or infer cautiously from the request. Distinguish at least between Apple II/II+, IIe, and enhanced IIe behavior when ROM, keyboard, 80-column support, mouse support, or firmware entry points matter.

## Control `apple2ts`

Read [references/apple2ts-api.md](references/apple2ts-api.md) before sending emulator requests.

Follow this workflow:

1. Confirm the server is local and reachable.
2. Do not guess endpoint names; treat [references/apple2ts-api.md](references/apple2ts-api.md) as authoritative.
3. Start exploratory sessions with `GET /api/machine`.
4. Use `GET /api/drives` only when drive or media state matters.
5. Read machine state before mutating it.
6. Use the smallest API call that solves the problem.
7. Re-read state after important mutations such as boot, reset, mount, memory writes, CPU changes, breakpoint changes, or save-state restore.
8. Prefer save-state export or snapshots before invasive debugging when reversibility matters.
9. To run an AppleSoft BASIC program, unmount all to avoid boot priority, and restart and reset to ensure a clean state, and then mount the BASIC file.

Use `curl` examples from the reference as a baseline. When automating text entry, prefer `/api/input/keys` with `type: "text"` for whole strings and `type: "key"` or `type: "keyCode"` for precise keypresses.

When mounting media, be explicit about the drive id:

- `fd1`, `fd2` for floppies
- `hd1`, `hd2` for hard drives

When the task touches CPU, memory, soft switches, or breakpoints, assume the user wants debugger-grade precision and verify resulting state instead of trusting a single write.

## Handle Disk Images With `a2kit` Or AppleCommander

Read [references/disk-images.md](references/disk-images.md) before changing Apple II disk images.

Prefer `a2kit` when:

- You need a scriptable CLI with explicit subcommands
- You need to create, inspect, copy into, copy out of, or tokenize content for many image types
- You want predictable command composition in pipelines

Prefer AppleCommander when:

- You need straightforward image listing, extraction, import, or image creation
- The local machine already has the `ac` CLI or an AppleCommander jar wired up
- You want a conservative tool for common DOS 3.3 or ProDOS image operations

Default workflow:

1. Identify the image format and likely filesystem.
2. Catalog or inspect the image before editing it.
3. Export or copy files out before destructive changes when the image is important.
4. Use the smallest operation that solves the task.
5. Re-catalog or verify the image after writes.
6. If the resulting image is meant for emulation, mount or boot-test it when possible.

Be explicit about the distinction between:

- Container format: `.dsk`, `.do`, `.po`, `.woz`, `.nib`, `2mg`
- Filesystem or OS convention: DOS 3.3, ProDOS, Pascal, CP/M

Do not imply that a file extension alone fully identifies the filesystem semantics.

## Write AppleSoft BASIC

Prefer AppleSoft BASIC for small Apple II programs, demos, text UI programs, integer/float calculations, simple graphics, and disk-driven workflows where interpreted code is acceptable.

Default practices:

- Start line numbers at `10` and increment by `10` unless the user requests dense numbering.
- Keep each line short enough to remain readable on 40-column displays.
- Use `HOME`, `HTAB`, `VTAB`, `INVERSE`, `NORMAL`, `POKE`, `PEEK`, `CALL`, `GOSUB`, and `ONERR` only when the target machine and side effects are understood.
- Mention machine assumptions when using soft switches, firmware entry points, mouse cards, 80-column firmware, ProDOS helpers, or slot-dependent I/O.
- If the user wants something loadable into an emulator or on disk, provide plain source first unless they explicitly ask for tokenized output.

When debugging BASIC, inspect:

- Syntax and token spacing issues
- Line-number flow
- Uninitialized variables
- Array bounds
- Dependence on specific ROM or peripheral behavior

## Write 6502 Assembly With `ca65`

Read [references/toolchains.md](references/toolchains.md) before choosing commands.

Default to portable, readable `ca65` assembly:

- Use labels instead of hard-coded branch offsets.
- Separate zero-page, code, data, and string areas clearly.
- Comment non-obvious hardware accesses or firmware entry points.
- State the expected load address, machine family, and DOS/ProDOS assumptions.

Prefer `cl65 -t apple2` when the user needs a simple build command quickly. Drop to `ca65` plus `ld65` only when the build needs custom segments, linker config, or mixed-language control.

When using firmware vectors, soft switches, or slot ROM entry points, call out the machine dependency explicitly instead of implying universality across the Apple II family.

## Write Apple II C With `cc65`

Use `cc65` or `cl65` for larger structured programs, mixed C/assembly projects, or code that benefits from libraries and cross-compilation.

Default practices:

- Prefer `cl65 -t apple2` for simple one-file programs.
- Keep memory use modest and avoid assuming large heap availability.
- Avoid desktop-style standard-library assumptions; confirm whether console, file I/O, or joystick support exists for the selected target/runtime.
- Use small, fixed buffers where possible.
- Drop to assembly for hot loops, firmware hooks, or hardware register access that is awkward in C.

If the user asks for C that talks directly to Apple II hardware, document which addresses or ROM calls are being used and why.

## Explain Hardware And Firmware

Read [references/hardware-and-firmware.md](references/hardware-and-firmware.md) for concise machine guidance.

When answering hardware questions:

1. Name the exact model or likely model.
2. Separate universal 6502-era concepts from model-specific behavior.
3. Distinguish motherboard/ROM features from add-in card features.
4. Note when DOS 3.3, ProDOS, language cards, RamWorks, 80-column cards, or mouse cards change the answer.

Prefer precise statements about slots, ROM, soft switches, keyboard behavior, video modes, and storage formats over generic nostalgia summaries.

## Use References Deliberately

Load only the reference needed for the current task:

- `references/apple2ts-api.md` for emulator HTTP control
- `references/disk-images.md` for `a2kit` and AppleCommander image workflows
- `references/toolchains.md` for `ca65`/`cc65`/`cl65` build patterns
- `references/hardware-and-firmware.md` for Apple II family hardware and firmware facts
