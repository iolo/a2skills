---
name: a2-a2kit
description: Default Apple II disk-image skill. Inspect, create, convert, extract from, copy into, or modify disk images with a2kit. Use for scriptable workflows involving .dsk, .do, .po, .woz, .nib, 2mg, DOS 3.3, ProDOS, Pascal, CP/M, tokenized BASIC, and repeatable disk-image automation.
---

# A2 A2Kit

## Overview

Act as a practical Apple II disk-image operator using `a2kit`. Prefer `a2kit` for disk-image work unless the user explicitly asks for AppleCommander or `a2kit` is unavailable. Prefer scriptable, verifiable commands and inspect images before editing them.

## References

Load only the reference needed for the task:

- [references/a2kit.md](references/a2kit.md) for scriptable disk-image workflows with `a2kit`
- [references/applecommander.md](references/applecommander.md) only when the user asks for AppleCommander, `a2kit` is unavailable, or comparing/falling back
- [references/appledos.md](references/appledos.md) for DOS 3.3 details
- [references/prodos.md](references/prodos.md) for ProDOS details

## Workflow

1. Use `assets/a2kit` when present and executable. If it is missing, fall back to AppleCommander when available.
2. Identify the image container format and likely filesystem.
3. Catalog or inspect the image before editing it.
4. Export or copy files out before destructive changes when the image is important.
5. Use the smallest operation that solves the task.
6. Re-catalog or verify the image after writes.
7. If the image is meant for emulation, mount or boot-test it when possible.

Be explicit about the distinction between container format (`.dsk`, `.do`, `.po`, `.woz`, `.nib`, `2mg`) and filesystem or OS convention (DOS 3.3, ProDOS, Pascal, CP/M). Do not imply that an extension alone fully identifies filesystem semantics.
