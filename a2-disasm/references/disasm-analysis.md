# Apple II disassembly: analysis and evidence

## Storage before opcodes

Fingerprint each supplied image and distinguish canonical inputs from manuals,
other releases, cracked variants, and remakes. Preserve conflicting information
with its source; a manual for another platform does not settle binary behavior.

Keep these coordinate systems separate:

| Coordinate | What must accompany it |
| --- | --- |
| Image byte offset | Image hash and container interpretation |
| Track/sector or block | Logical/stored/controller order and mapping |
| File offset | Allocated stream versus logical EOF or payload |
| Runtime address | Module, phase, bank, transform, and entry context |

For ordinary files, preserve name, type, auxiliary/load address, EOF, and relevant
volume/directory metadata. Follow allocation chains rather than trusting catalog
counts alone. For custom loaders, reconstruct the actual sector sequence and
destination writes. A 143,360-byte image suggests geometry; it does not establish
a filesystem or sector order. A recognizable sector permutation likewise does
not prove that the disk uses DOS.

Test competing orderings reversibly using loader tables, cross-sector routines,
absolute references, and exact reconstruction. Keep physical controller sector
IDs distinct from image-file positions. Avoid converting the only input in place.

## Loader and memory atlas

For each load, record the source spans in read order, destination ranges, bank
state, transform chain, entry points, outgoing loads, and bytes overwritten by
later reads. Keep overwritten stored spans even when absent from final RAM.
An effective memory dump cannot recover their original contents.

Follow boot stages before treating filesystem files as the whole program.
Resident DOS/RWTS, raw track overlays, auxiliary RAM, language-card banks,
and controller-downloaded code can all fall outside a simple file listing.
An OS load address may describe staging rather than final placement. Identical
addresses in mutually exclusive overlays need distinct symbols and provenance.

For encoded regions, derive the transform from the loader or a supported
consumer and verify both directions. Retain stream position when splitting a
stateful transform into components. A decoder that produces plausible opcodes
is weaker evidence than a matching loader, valid control flow, and an inverse
that restores the stored bytes. Do not invent bytes beyond the disk read when
runtime relocation or swapping touches adjacent RAM.

## Native control-flow recovery

Use `da65` or another available decoder for bounded candidate regions after
establishing origin and CPU. For example, with a proven raw payload at $0800:

```sh
da65 --cpu 6502 --start-addr 0x0800 -o build/candidate.s build/payload.bin
```

This command produces a comparison listing, not authoritative recovered source.
Keep generated output away from curated files and do not regenerate over edits.

During promotion, inspect these common boundary traps:

- A `JSR` may be followed by text, OS parameters, or private inline arguments.
  Follow how the callee changes the saved return address to find continuation.
- A pointer table's lookup base may precede its visually obvious start. Recover
  the full index domain from consumers; initial entries can overlap preceding
  instructions or another table. Preserve non-callable sentinel entries.
- Self-modifying stores may target instruction operands. Name the operand and
  patch sites and distinguish stored bytes from runtime patched values.
- Multiple entries may interpret the same bytes differently, including `BIT`
  prefixes that consume instructions on another path. Preserve both paths and
  emit each byte once rather than forcing a false linear partition.
- Apparent `BRK`, illegal opcodes, or implausible branches can indicate data,
  a wrong origin, a patch target, or the wrong processor. Confirm per-region
  6502/65C02/65816 requirements, including downloaded peripheral programs.
- Fixed-address reconstruction requires the original addressing mode and operand
  width. Check assembler listings for silent zero-page shortening, altered
  branch layout, and changed alignment; use explicit widths where needed.

Use source labels for proven roles and neutral address/field names for unresolved
ones. Comments should explain behavior and evidence, not turn inferred original
intent into a fact. Distinguish retained/unreachable instructions from live code;
absence of a known caller alone does not classify bytes as data.

## Interpreters and mixed code

Treat Pascal p-code and custom game scripts as executable languages with their
own entries, dispatch tables, operand widths, branches, strings, and metadata.
Inventory their procedures/records separately from the native interpreter.
Do not apply a 6502 decoder to an entire binary-typed file or classify every
interpreter input as passive data.

For Pascal, establish the shipped interpreter version and actual handlers before
trusting an external opcode table. Preserve variable-width operand choices,
procedure attributes, backwards jump references, alignment, native procedures,
and relocation records. Named assembler macros can reconstruct p-code exactly
without assuming a historical compiler will reproduce its instruction choices.
Prove one bounded procedure before scaling the decoder.

For text or compact custom scripts, connect vocabulary and operation names to
the interpreter dispatch and state consumers. High-bit text may be source-like
instructions. Keep decoded text, control bytes, and script structure distinct;
do not promise script editing if only a read-only view has been implemented.

## Gameplay mechanics as evidence

Trace a value from table or initialization through its consumers and state
transitions. A useful evidence record includes:

| Field | Purpose |
| --- | --- |
| ID, claim, status | Stable reference; observed, derived, hypothesis, or assumption |
| Input hash and location | Exact release, stored span, module/bank/address |
| Basis | Instructions, table indexing, callers, or recorded runtime event |
| Reproduction | Command, fixture, or trace with relevant tool/build identity |
| Units and limits | Representation, conditions, unresolved conversions |

Keep counters in update calls, coordinates in native units, and signed/fixed-point
or packed-BCD representations explicit. CPU frequency alone does not establish
updates per second: conditional paths, disk waits, rendering, and frame pacing
matter. A zero low-nibble test establishes one failing nibble value, not a
measured 1/16 event probability without distribution evidence.

Join related object tables across the complete type domain before assigning
roles. Separate acquisition thresholds, movement, collision envelopes, damage,
visual aftermath, lifetime, and reload cadence. A visible effect is not evidence
of area damage. Record manual/binary conflicts without silently choosing a
normalization for a future remake.

If a dynamic probe is needed and within the authorized scope, state the question,
breakpoint/watchpoint, expected discriminating observation, and bounded capture.
Prefer load boundaries and specific consumers to huge undirected traces. Record
bank mapping with CPU-visible memory, especially auxiliary zero page. Resume
only after capturing the state needed to reproduce the conclusion.
