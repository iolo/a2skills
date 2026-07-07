# a2kit

Use this reference when the task needs scriptable Apple II disk-image inspection, creation, conversion, or file transfer.

## Agent Navigation

- Prefer a bundled executable at `assets/a2kit` when present and executable.
- Prefer `a2kit` for Apple II disk-image work when it is available.
- Use `applecommander.md` only when the user specifically asks for AppleCommander/`ac`, `a2kit` is unavailable, or a conservative common DOS/ProDOS workflow is clearly simpler.
- Use `appledos.md` or `prodos.md` for BASIC-facing DOS/ProDOS command syntax.
- After modifying an image, recatalog it and boot or mount-test it when possible.

## Best fit

Prefer `a2kit` when:

- the workflow should be repeatable or scriptable
- the task needs explicit subcommands and predictable CLI composition
- the task involves format conversion or filesystem-aware inspection
- the task needs tokenization, detokenization, or structured output

## Supported image and filesystem scope

Disk image support includes:

- `2MG`
- `D13`
- `DO`
- `DSK`
- `IMD`
- `IMG`
- `NIB`
- `PO`
- `TD0`
- `WOZ`

Filesystem support includes Apple DOS 3.2, Apple DOS 3.3, ProDOS, CP/M, and UCSD Pascal.

## High-value commands

Useful installed commands from `a2kit --help`:

- `catalog`
- `tree`
- `stat`
- `geometry`
- `mkdsk`
- `cp`
- `get`
- `put`
- `mkdir`
- `delete`
- `rename`
- `retype`
- `tokenize`
- `detokenize`
- `verify`
- `renumber`

## Common workflows

Catalog an image:

```sh
a2kit catalog --dimg demo.dsk
```

Inspect filesystem tree as JSON:

```sh
a2kit tree --dimg demo.po
```

Create a new DOS 3.3 image:

```sh
a2kit mkdsk -o dos33 -v 254 -t woz2 -d demo.woz
```

Create a new ProDOS image:

```sh
a2kit mkdsk -o prodos -v DEMODISK -t woz2 -d demo.woz
```

Smart-copy a local BASIC file into an image:

```sh
a2kit cp -a 2049 hello.bas demo.dsk
```

Extract a file from an image:

```sh
a2kit get -d demo.dsk -f HELLO
```

Tokenize AppleSoft text:

```sh
a2kit tokenize -a 2049 -t atxt < hello.bas > hello.atok
```

Detokenize AppleSoft from an image:

```sh
a2kit get -d demo.dsk -f HELLO -t atok | a2kit detokenize -t atok
```

## Practical cautions

- Back up important images before mutating them.
- Determine whether the image is DOS 3.3, ProDOS, Pascal, or another layout before assuming filename rules or file types.
- Distinguish tokenized AppleSoft files from plain text listings.
- Prefer JSON or machine-readable output when a later step will parse results.
- After writes, recatalog the image and, if relevant, mount it in an emulator to confirm bootability or file visibility.
