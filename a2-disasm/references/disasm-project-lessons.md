# Lessons from four local disassembly projects

These cases were distilled from the user's repositories on 2026-10-14. The
paths below identify further evidence when those checkouts are available; they
are not installation or runtime dependencies. Project-specific addresses,
accepted exceptions, and investigation permissions are examples, not defaults.
Some project documents retain historical checkpoints; check their current
source, receipts, and explicit limits before quoting a completion claim.

## Carmen Sandiego World: files, revisions, and overlays

Repository: `apple2-carmen-sandiego-world-disasm` under
`/home/iolo/workspace/retro/`.

Evidence: `docs/reconstruction.md`, `docs/source-guide.md`,
`docs/verification.md`, `tools/emit_source.py`, and `tools/case_state.py`.

- Fresh ProDOS disks are checked at file/metadata level; allocation and unused
  space can differ. The floppy pair and 800 KB release are related variants,
  not interchangeable images. Share source only for verified identical modules.
- N and R both load at $6000 in different phases. Auxiliary-memory staging and
  language-card services make a file's load address an incomplete memory map.
- Mechanical Q disassembly mistook patched store operands for apparent BRK/JSR
  instructions. Z includes 6502, 65C02, and 65816 regions and a downloaded
  controller program; a global 6502 assumption misdecodes it.
- The case snapshot contains stale route slots; its roster resume flag is
  independent of whether the snapshot page contains data. Lossless structured
  editing must preserve both facts.
- HGR phase bits and invisible bytes, overlapping compressed picture streams,
  dictionary tokens, and pronoun markers matter beyond preview appearance.
  The initial listing generator preserves curated files unless forced.

Transfer: establish release/module identity and loader state before naming
addresses, and distinguish editable source from convenient decoded views.

## Mask of the Sun: custom semantics behind a DOS catalog

Repository: `apple2-mask-of-sun-disasm` under the same local parent.

Evidence: `docs/disk-layout.md`, `docs/engine.md`, `docs/build.md`,
`docs/pictures.md`, `docs/validation.md`, and `tools/verify_checkout.py`.

- Catalog sizes include anomalies; allocation follows TS chains. Binary-typed
  vector files do not carry ordinary DOS binary headers. The custom loader
  reads allocated sectors and deliberately includes headers in other files.
- High-bit ULTRA room/library text is interpreted program logic. Native
  interpreter, intrinsic, font-renderer, boot, DOS, and RWTS code require
  separate ownership; filenames alone do not classify contents.
- Side B retains a different DOS fragment while live files occupy other sectors
  in the same tracks. Assembling a full variant does not authorize placing all
  of it over the disk's live allocations.
- Native save writes tracks 23–31 as a RAM snapshot. Catalog-only verification
  would miss the save footprint and fresh-boot restore behavior.
- Editable vectors use constrained SVG geometry; browser rendering is an
  approximation. Native renderer fixtures verify pictures, while ordinary game
  replays separately verify loading, timed interactions, and ending routes.
- Repeated blank-image builds and read audits distinguish reconstruction from
  copying original code/image exports. The clean committed-tree audit excludes
  uncommitted changes, a significant validation boundary.

Transfer: follow consumers over filesystem labels, preserve disk ownership, and
test both standalone construction and the actual supported editing path.

## Rescue Raiders: static evidence and native units

Repository: `apple2-rescue-raiders-disasm` under the same local parent.

Evidence: `DISASSEMLY.md` (the repository's spelling), `src/README.md`,
`evidence/evidence.jsonl`, `evidence/dynamic-escalations.md`, and
`tools/recover.py`.

- A catalog failure led to custom-loader recovery, not rejection of the image.
  Boot relocation and selector streams establish read order and runtime load
  identities. DOS-logical ordering does not imply a DOS filesystem.
- Later loads overwrite earlier asset spans. Preserve both the stored read
  provenance and the final effective bank used for sprite extraction.
- Constructor and destruction table lookup bases overlap preceding bytes.
  Full-domain indexing corrected shifted object roles; a plausible list of
  pointers was insufficient evidence for assigning gameplay types.
- Update-wrapper counts, native coordinates, and conditional entropy tests are
  exact static results. Seconds, screen-unit normalization, and actual event
  probabilities remain separate measurements. Manual claims can conflict with
  internal representation without either value being silently discarded.
- Exact whole-disk repacking coexists with unpromoted extracted loads. The
  source and mechanics completion boundaries remain independent of disk hashes.
  Runtime use is explicitly gated in this project; that policy is not imported
  into every disassembly task.

Transfer: pair semantic names with consumer evidence and units; distinguish
source-exact slices, retained bytes, and runtime observations in delivery claims.

## SunDog: mixed languages and disk-wide accounting

Repository: `apple2-sundog-disasm` under the same local parent.

Evidence: `docs/pcode-toolchain.md`, `docs/runtime-architecture.md`,
`docs/encoded-native-overlay.md`, `docs/strict-build.md`,
`docs/classification-ledger.md`, and `docs/user-assumed-data.md`.

- Pascal segments, native procedures, resident runtime, raw overlays, and custom
  dialogue instructions need separate decoders. The shipped interpreter settles
  opcode semantics and operand widths more reliably than a nominal UCSD table.
- ca65 macros preserve p-code encodings, procedure metadata, and jump references
  without depending on a historical Pascal compiler's code generation.
- Encoded banks are assembled as decoded code then inversely transformed for
  storage. Fragment encoding must retain stream phase. A swap can touch bytes
  beyond the original read; those runtime bytes cannot be invented from disk.
- A ledger maps component classification to every physical disk occurrence,
  separating source ownership from code/data evidence and repeated placements.
- Strict builds exclude temporary dependencies, but that check alone cannot
  prove classification. The user's bounded 488-byte assumption is separately
  recorded and hash-checked; it remains an assumption, not identified data and
  not precedent to stop investigating other projects' tails.

Transfer: make interpretation, source authority, physical coverage, and accepted
uncertainty independently inspectable, especially for mixed-language disks.
