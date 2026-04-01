# Toolchains

Use this reference when writing or building Apple II code with AppleSoft BASIC, `ca65`, `cc65`, or `cl65`.

## Installed tools on the authoring machine

The machine used to create this skill had these binaries available:

- `/usr/bin/ca65`
- `/usr/bin/cc65`
- `/usr/bin/cl65`

Do not assume they exist on every future machine. Verify before building.

## AppleSoft BASIC

Prefer plain text listings unless the user explicitly asks for tokenized binaries or disk images.

Default formatting:

- Line numbers: `10`, `20`, `30`, ...
- Uppercase keywords for readability
- Short lines for 40-column display compatibility

Minimal example:

```basic
10 HOME
20 PRINT "HELLO, APPLE II"
30 END
```

When the user wants to inject BASIC into `apple2ts`, the API can mount `basic-text` directly. See `apple2ts-api.md`.

## Fast path builds with `cl65`

Use `cl65` when the user mainly wants a working Apple II binary with minimal ceremony.

C example:

```sh
cl65 -t apple2 hello.c -o hello
```

Assembly example:

```sh
cl65 -t apple2 hello.s -o hello
```

This is the safest default when you do not need a custom linker config.

## Split builds with `ca65` and `ld65`

Use separate assemble and link steps when the project needs custom object composition, segment control, or mixed-language builds.

Typical flow:

```sh
ca65 hello.s -o hello.o
ld65 -t apple2 hello.o -o hello
```

If a custom linker config is required, add `-C path/to/config.cfg` to `ld65`.

## Mixed C and assembly

Use `cl65` for the final link when combining C and assembly files:

```sh
cl65 -t apple2 main.c helper.s -o program
```

Keep assembly interfaces simple and document calling conventions, clobbered registers, and memory ownership.

## Practical coding guidance

### 6502 assembly

- State the expected load address.
- Distinguish ROM calls from DOS or ProDOS entry points.
- Use labels and constants instead of raw magic numbers when possible.
- Comment soft-switch accesses and slot-dependent I/O.

### C with `cc65`

- Keep stack and heap assumptions conservative.
- Prefer fixed-size buffers.
- Avoid heavy libc assumptions.
- Drop into assembly for hardware-facing routines or tight loops.

## Machine targeting

`-t apple2` is the obvious baseline, but machine-family differences still matter at runtime:

- Apple II and II+ differ from IIe-family ROM and peripheral assumptions.
- 80-column, mouse, and auxiliary-memory workflows are much more IIe-centric.
- If the code depends on enhanced IIe behavior, state that explicitly in comments and user-facing notes.

## Verification

After building:

1. Check the tool exited successfully.
2. Identify the produced output file.
3. If an emulator is available, boot or mount the result and verify expected behavior.
4. If runtime behavior depends on slot cards, ROM version, or memory expansion, say so explicitly.
