# AppleCommander

Use this reference when the task needs straightforward Apple II disk-image listing, extraction, import, or simple image creation with AppleCommander.

## Agent Navigation

- Prefer an explicit executable, then a platform-compatible skill-local bundle, then `ac` on PATH. Root repository assets are not installed with this skill.
- Prefer `a2kit.md` for general disk-image automation.
- Use this file when the user asks for AppleCommander/`ac`, `a2kit` is unavailable, or the task is simple image listing, extraction, import, or creation.
- Use `appledos.md` or `prodos.md` for BASIC-facing DOS/ProDOS command syntax.
- After modifying an image, recatalog it and boot or mount-test it when possible.

## Best fit

Use AppleCommander when:

- the user explicitly asks for AppleCommander or `ac`
- `a2kit` is unavailable and AppleCommander is available
- the workflow is straightforward and interactive rather than highly scripted
- the task is simple listing, extraction, import, or image creation
- conservative DOS 3.3 or ProDOS operations are enough

## High-value commands

Useful commands:

- `-i` image info
- `-ls`, `-l`, `-ll` image directory listings
- `-lsj`, `-lj`, `-llj` JSON directory listings
- `-e` export a file
- `-x` extract all files
- `-g` get a raw file
- `-p`, `-pt`, `-ptx` put a file into an image
- `-d` delete a file
- `-k`, `-u` lock or unlock a file
- `-n` rename a ProDOS or Pascal volume
- `-dos140`, `-pro140`, `-pro800`, `-pas140`, `-pas800` create images
- `-convert` convert or unpack some container formats
- `-bas` import AppleSoft BASIC text into tokenized format

## Common workflows

List a disk:

```sh
ac -ls demo.dsk
```

Get detailed JSON listing:

```sh
ac -llj demo.po
```

Extract one file:

```sh
ac -e demo.dsk HELLO hello.out
```

Extract all files:

```sh
ac -x demo.dsk extracted
```

Create a 140K DOS 3.3 image:

```sh
ac -dos140 demo.dsk
```

Create a 140K ProDOS image:

```sh
ac -pro140 demo.po DEMODISK
```

Import text as AppleSoft BASIC:

```sh
ac -bas demo.dsk HELLO < hello.bas
```

Import plain text with TXT defaults:

```sh
ac -pt demo.dsk README < readme.txt
```

## Practical cautions

- Back up important images before mutating them.
- Determine whether the image is DOS 3.3, ProDOS, Pascal, or another layout before assuming filename rules or file types.
- Prefer JSON listings when a later step will parse results.
- After writes, recatalog the image and, if relevant, mount it in an emulator to confirm bootability or file visibility.

## Verified BASIC round trip

Work on a new writable copy of a bootable base image; leave its startup files
intact. From the directory containing `hello.bas` and the copied `demo.dsk`:

```sh
ac -bas demo.dsk DEMOBAS < hello.bas
ac -e demo.dsk DEMOBAS listing.bas
ac -llj demo.dsk
```

Boot DOS and use `RUN DEMOBAS`. The repository tests compare this tokenized
payload with a2kit's output. AppleCommander 13.0 was checked locally. For
cc65 AppleSingle BIN import use `ac -as demo.dsk DEMOC < hello.as`; do not import
its header as raw program bytes.
