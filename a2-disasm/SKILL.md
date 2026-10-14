---
name: a2-disasm
description: Reverse engineer Apple II programs and disk images into evidence-backed disassembly, buildable source, decoded assets, and reproducible disk rebuilds. Use for 6502 loader and overlay analysis, mixed native/interpreted code, code/data classification, and recovery of gameplay mechanics from existing binaries; use a2-cc65 for new native program development.
---

# A2 Disasm

For Windows/macOS setup, shell syntax, and emulator limitations, read
[references/host-platforms.md](references/host-platforms.md) when needed.

Recover what the supplied program actually does, with a traceable path from
disk bytes through runtime mappings to readable source and verified outputs.
Scale the work to the request: a routine explanation does not require a whole
disk reconstruction.

## Establish the target

- Read the project's instructions, existing evidence, build tools, and current
  source ownership before generating anything. Preserve curated source; put
  mechanical listings and investigation output in a separate generated area.
- Identify the exact release by filename, size, and hash. Keep originals
  unchanged and use disposable media for emulation and saves. Related releases
  may share some modules while differing in loaders, data, and CPU requirements.
- Distinguish the requested result: analysis, incremental recovery, source-only
  rebuild, exact disk reproduction, or validated behavioral equivalence. Keep
  accepted external system dependencies and unresolved regions explicit.
- Honor the project's existing emulator and investigation constraints. A
  static-only or approval-gated policy in one reference project is not a default
  for other projects. Do not broaden disassembly into a port or remake.

## Core workflow

1. **Inventory storage and loading.** Establish container, sector/block order,
   filesystem if any, boot path, file allocation, and raw reads. Catalog failure
   does not establish invalid media; a binary file type does not establish a
   standard load header. Record both stored extents and effective loaded bytes.
2. **Map runtime identities.** Key locations by release, module/load phase,
   memory bank, and address. Follow staging, relocation, decompression, decoding,
   overlays, and self-modification before trusting disassembler origins.
3. **Classify from consumers and control flow.** Start at evidenced entries and
   dispatch targets. Separate native instructions, interpreted instructions,
   inline parameters, tables, assets, workspace, and unresolved bytes. Linear
   disassembly is triage, not proof that a region is executable.
4. **Promote bounded regions.** Give routines meaningful names and document
   inputs, outputs, flags, clobbers, shared state, and callers where supported.
   Preserve exact instruction encodings, fixed addresses, overlapping uses,
   and patched operands. Assemble and compare each promoted region promptly.
5. **Recover editable assets when requested.** Identify the authoritative
   representation and write a lossless inverse. Retain padding, phase bits,
   stale fields, and original packing when required. Verify that edits reach
   the build; a decoded preview alone is not an editable source asset.
6. **Verify the actual claim.** Separate extraction round trips, source assembly,
   complete disk accounting, independent builds, and runtime observations.
   Report gaps and assumptions alongside the result.

## Read only the relevant reference

- [Analysis and evidence](references/disasm-analysis.md): disk ordering, loader
  maps, native and interpreted control flow, and gameplay-mechanics recovery.
- [Rebuilds, assets, and validation](references/disasm-reconstruction.md): source
  authority, lossless codecs, coverage accounting, clean builds, and emulator
  comparisons.
- [Lessons from the four projects](references/disasm-project-lessons.md): concrete
  failure modes and local source-document pointers for further investigation.

## Evidence and completion

For a material claim, record the input identity, disk offset and runtime context,
supporting instructions or consumer, and a reproduction command or trace receipt.
Distinguish observed behavior, static derivation, hypothesis, and explicit user
assumption. Unknown values remain unknown rather than acquiring plausible names
or normalized units.

Report these dimensions independently when relevant:

- Byte equality and the comparison scope: payload, file metadata, or whole disk.
- Source ownership and remaining opaque/temporary dependencies.
- Code/data classification and remaining semantic uncertainty.
- Runtime checkpoints actually observed, including the tested build identity.

Neither `.byte` declarations nor removal of `INCBIN` proves understanding.
Source-built totals include data declarations. A passing build does not imply a
boot test, and a boot test does not establish gameplay or save/reload coverage.

## Companion routing

When available, use `a2-a2kit` for filesystem extraction and packaging,
`a2-cc65` for assembler/linker mechanics, `a2-basic` for tokenized BASIC, and
`a2-hardware` for machine, ROM, banking, and soft-switch details. Use
`a2-apple2ts`, `a2-mame`, or `a2-gssquared` for runtime investigation, honoring an
explicit emulator choice. Otherwise prefer configured Apple2TS MCP when suitable.
These companions provide tool-specific operations; this skill owns the evidence
and reconstruction workflow. No emulator is required for static analysis.
