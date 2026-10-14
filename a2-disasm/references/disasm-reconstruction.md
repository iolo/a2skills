# Apple II reconstruction, assets, and validation

## Choose the equality contract

| Contract | Required comparison |
| --- | --- |
| Extract/repack | Every extracted span maps back to the original bytes |
| Module/source exact | Assembled payload and any storage transform match the target |
| Filesystem equivalent | Complete intended files, contents, EOF, types, load addresses, and relevant metadata |
| Disk exact | Every stored byte, including allocation metadata and unused regions |
| Behavior equivalent | Documented differences plus relevant runtime comparisons |

Fresh ProDOS allocation can satisfy a file-level contract without matching disk
hashes. Conversely, a repack made from raw sectors can match every byte while
recovering no source. State which contract applies; preserve custom disk layout
when raw reads, checksums, or save routines depend on it.

## Authority and coverage

Separate extraction from normal building. Mark inputs as curated source,
editable asset, identified retained data, accepted external dependency, or
temporary unresolved material. Decoded reports and raw comparison exports may
be reference-only. Do not hide temporary dependencies by renaming them as assets,
large `.byte` blocks, encoded strings, or generated includes.

An incremental rebuild may retain opaque regions when consistent with the task.
Make that status visible and provide a strict completion check when a full
source rebuild is required. Explicit user exceptions remain assumptions with
their exact byte ranges and hashes; they do not become classification evidence.

For disk construction, use a placement manifest and empty output storage for
the selected full-rebuild scope. Check source slice bounds, destination bounds,
lengths, gaps, collisions, and ownership. Shared source can feed several mapped
occurrences; overlapping writes require an explicit ordering or equality rule.
Preserve exact metadata anomalies when the contract requires them rather than
silently repairing the disk.

Track independent coverage measures:

- Source-built, asset/data, external, and temporary disk occurrences.
- Evidence-backed code/data classification, including unresolved or assumed spans.
- Unique source components versus repeated disk placements and runtime loads.

Do not count duplicate overlays as newly understood unique bytes. Do not equate
source-built bytes with instruction bytes. For execution overlaps, record both
interpretations without double-counting physical storage.

Use linker maps, listings, and size/address assertions to preserve module
boundaries. Compare the assembled region before placement, then the produced
file or disk. Keep provenance checks separate from build input reads: an original
image may be a comparison oracle without being required to construct output.

## Editable assets and faithful inverses

Find consumers before deciding the format. Recover dimensions, pointer bases,
record boundaries, compression markers, count semantics, and drawing order.
Make authoritative inputs obvious so editing a PNG/JSON/SVG cannot silently
leave an old packed binary in charge of the build.

- **HGR and sprites:** retain high phase bits, invisible row bits, interleaved
  screen layout, page holes, signed offsets, and stored tails. A monochrome
  preview is not a complete representation of artifact color or raw storage.
- **Compressed images:** retain literal/repeat distinctions and packing when
  exact stored output matters. Equal decoded pixels do not guarantee equal
  compressed bytes. Test zero-count behavior, overlapping records, and strides
  against the native decoder rather than imposing host conventions.
- **Vector pictures:** preserve plot-before/after-move order, byte wrapping,
  scale, fill seeds, layer order, and native coordinate units. A convenient SVG
  preview can differ from native edge fill or artifact colors. Document the
  supported edit subset and reject unsupported transforms or capacity overflow.
- **Text and saves:** retain high bits, control bytes, dictionary token choices,
  separators, empty entries, padding, unset sentinels, and stale slots. A populated
  save page may be inactive if a separate resume flag is clear. Expose those
  fields separately rather than normalizing them away.
- **Sound and procedural graphics:** recover generators and parameters when
  there is no stored bitmap or audio stream. Literal `$C030` bytes can occur in
  inert data; prove executed speaker accesses. WAVs are previews or recordings,
  not automatically native sound assets. Declare any clock/filter assumptions.

Test `encode(decode(original)) == original` for lossless formats. Also test a
small supported edit through the actual build and relevant consumer; round-trip
equality alone can pass even when the editable fields are ignored. Restore
baseline assets before accepting baseline hashes or gameplay comparisons.

## Independent builds

For a claimed standalone source rebuild, build in a fresh staging tree with the
declared source/assets/configuration and required classification documents.
Exclude original disks, reference-only binary exports, and previous output.
Build twice into distinct empty output directories and compare disk outputs
and deterministic reports. Remove incidental timestamps from generated listings
or distinguish them from semantic output when reporting reproducibility.

When hidden dependencies are plausible, inspect actual file reads (for example
with `strace` on Linux) as well as declared manifests. Classify reads of toolchain
libraries separately from forbidden reference inputs. A clean-checkout audit
must state whether it tested the committed revision or current uncommitted work.
Do not claim it validated edits absent from the staged tree.

## Runtime evidence

Use isolated copies of original and rebuilt disks with matching machine, ROM,
RAM, controller, slot, and timing settings. Record image hashes and build identity.
Keep save media disposable: a game's save may write raw sectors rather than a
catalog file. Never use preservation inputs as writable save targets.

Choose checkpoints that exercise the changed scope: boot/load handoffs, title,
gameplay transitions, disk swaps, death/restart, save, and fresh-session reload.
Compare internal state and native screen memory where useful, not only screenshots.
For sound, distinguish observed toggles, nonzero recording, and audible playback.
For timed input, synchronize to the consumer's readiness; a first-key timer and
a subsequent blocking line editor can require different delivery strategies.

Keep native renderer fixtures, injected memory/PC probes, restored checkpoints,
and ordinary cold-boot play separately labeled. A renderer called on a fixture
can prove an asset decoder without proving its normal loader or gameplay path.
Bound the probe and restore its baseline between cases.

Report PASS, FAIL, and SKIP with coverage limits. Byte-identical outputs may
reuse an earlier applicable runtime baseline if its machine and image identity
match; explicitly identify the reused evidence instead of claiming a new run.
