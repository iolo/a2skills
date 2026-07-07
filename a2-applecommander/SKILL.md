---
name: a2-applecommander
description: AppleCommander-specific Apple II disk-image skill. Use when the user asks for AppleCommander or ac, when a2kit is unavailable, or when a conservative common DOS 3.3/ProDOS listing, extraction, import, or image creation workflow is enough.
---

# A2 AppleCommander

## Overview

Act as a practical Apple II disk-image operator using AppleCommander. Prefer `a2kit` for general disk-image automation; use AppleCommander when explicitly requested, when `a2kit` is unavailable, or when its conservative DOS 3.3/ProDOS operations are the simplest fit.

## References

Load only the reference needed for the task:

- [references/applecommander.md](references/applecommander.md) for AppleCommander workflows
- [references/a2kit.md](references/a2kit.md) when deciding whether the default `a2kit` workflow is a better fit
- [references/appledos.md](references/appledos.md) for DOS 3.3 details
- [references/prodos.md](references/prodos.md) for ProDOS details

## Workflow

1. Confirm the user asked for AppleCommander/`ac`, or that `a2kit` is unavailable or a poorer fit.
2. Use `assets/ac` when present and executable. If it is missing, use another available AppleCommander command form.
3. Identify the image container format and likely filesystem.
4. List or inspect the image before editing it.
5. Extract files before destructive changes when the image is important.
6. Use the smallest import, export, or create operation that solves the task.
7. Re-list or verify the image after writes.

Be explicit about container format versus filesystem. Do not infer full semantics from `.dsk`, `.do`, `.po`, `.woz`, `.nib`, or `2mg` alone.
