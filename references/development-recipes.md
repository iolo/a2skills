# Source to disk to emulator

## Native examples

The installed `a2-cc65` skill contains `assets/examples/` and
`scripts/build_examples.py`. From that skill directory:

```sh
python3 scripts/build_examples.py --output-dir /tmp/a2-native
```

The output directory must be new. Optional `--source-dir`, `--cl65`, `--ca65`,
and `--ld65` select explicit inputs/tools. All intermediate files stay in the
output directory. No source directory writes or downloads occur.

| Output | Format and assumptions | Expected result |
| --- | --- | --- |
| `hello.as` | cc65 AppleSingle BIN, DOS/ProDOS and AppleSoft ROM | APPLE II C READY, waits for key |
| `mixed.as` | Same runtime; C calls a fastcall assembly routine | MIXED RESULT: 42, waits for key |
| `hello.bin` | Raw 6502, entry/load $0800; no OS/runtime | $0300=$42, $0400=$C1, loop at $0810 |

Default native runtime profile: 40-column IIe, main-memory text page 1. The C
runtime uses AppleSoft ROM routines and OS startup/exit state; do not treat it
as a standalone binary for an Integer BASIC ROM machine. The raw fixture uses
no stack calls or zero-page storage and works on the original Apple II.

Equivalent commands in a writable copy of the example sources:

```sh
cl65 -t apple2 -m hello.map -o hello.as hello.c
cl65 -t apple2 -m mixed.map -o mixed.as mixed.c twice.s
ca65 -o hello.o hello.s
ld65 -C raw.cfg -m raw.map -Ln raw.lbl -o hello.bin hello.o
```

`raw.cfg` explicitly fixes the raw load address. For standard cc65 outputs,
read AppleSingle's data fork and ProDOS metadata rather than stripping an
assumed header length. Check linker maps and labels when changing layouts.
The mixed helper receives/returns an unsigned byte in A, zeros X, preserves Y,
and clobbers flags. No shared zero-page scratch or memory ownership is needed.

## BASIC example

The installed `a2-basic` skill contains `assets/examples/hello.bas`. It prints
APPLE II BASIC READY, prompts for NAME, and prints HELLO followed by the input.
At an AppleSoft prompt, enter the numbered lines and RUN. GET is a blocking
single-character read; INPUT is appropriate here for an entire name.

To tokenize with a2kit:

```sh
a2kit tokenize -t atxt -a 2049 < hello.bas > hello.atok
a2kit detokenize -t atok < hello.atok > listing.bas
```

Whitespace may normalize during detokenization. Retokenizing should reproduce
the token stream. Tokenized BASIC needs a BASIC file type and interpreter; it
is not machine code to execute by setting PC.

## Disk packaging

From installed `a2-a2kit`, pass explicit paths to a source and **bootable** base
image. Root repository assets are optional conveniences, not installed dependencies.
Use a different new output directory for each call:

```sh
python3 scripts/package_disk.py --source /absolute/hello.bas --format basic \
  --base-image /absolute/dos33.dsk --output-dir /tmp/a2-basic-disk --name DEMOBAS
python3 scripts/package_disk.py --source /tmp/a2-native/hello.as --format applesingle \
  --base-image /absolute/prodos.po --output-dir /tmp/a2-c-disk --name DEMOC
python3 scripts/package_disk.py --source /tmp/a2-native/hello.bin --format raw \
  --address 0x800 --base-image /absolute/dos33.dsk \
  --output-dir /tmp/a2-raw-disk --name DEMORAW
```

Repeat the C command with `mixed.as` / DEMOMIX. Each format supports either
DOS 3.3 or ProDOS; use one fixture per copied disk when base images are nearly
full. `--a2kit /path/to/a2kit` overrides a compatible skill-local bundle or PATH.
The helper refuses an existing output directory or filename, malformed input,
unsupported filesystems, and out-of-range payloads. Output includes the verified
disk, extracted payload, metadata, catalog, manifest, and BASIC listing if relevant.

DOS BIN stores a little-endian address/length header; ProDOS BIN stores load
address in auxiliary metadata. The helper applies each filesystem convention
and compares the extracted data and metadata. BASIC uses DOS A / ProDOS BAS.
AppleSingle BIN payload and load address come from its entries.

These checks do not prove bootability. A formatted empty image is not necessarily
a boot disk. DOS needs installed DOS tracks/startup configuration; ProDOS needs
its system files and BASIC.SYSTEM for these recipes. Preserve startup files in
the supplied base. At the appropriate prompt use `RUN DEMOBAS`, `BRUN DEMOC`,
or `BRUN DEMOMIX`. The raw program loops forever; reset only the scratch session
after its verification. The package helper does not rewrite startup programs.

Common failures: wrong interpreter, disk full, filename collision, missing
BASIC.SYSTEM, AppleSingle header loaded as code, wrong load address, or bank/
video state inconsistent with the fixture. Diagnose those before changing code.

## Emulator handoff

Use `a2-apple2ts` for configured MCP sessions, `a2-mame` for Lua control, or
`a2-gssquared` for native Apple II/IIgs debug-socket control.
Preserve explicit emulator choice. Upload `hello.bin` as raw at $0800, set PC,
and stop at the linker label `done`; packaged runtime programs boot through DOS.
Compare marker bytes and visible text. Keep independent sessions and disk copies
for side-by-side runs; use matched enhanced-IIe profiles for runtime comparisons.

## Sources and tested tools

- [cc65 Apple II target and file formats](https://cc65.github.io/doc/apple2.html)
- [a2kit maintained CLI documentation](https://github.com/dfgordon/a2kit)
- [AppleCommander command line](https://applecommander.github.io/commandline/)

Validated locally with cc65 V2.19 git a028ac414, a2kit 4.4.2, AppleCommander
13.0. See the repository verification commands for repeatable checks. Validate
the installed tool version rather than assuming all releases share syntax.
