# Disk Images

Use this reference when the user wants to inspect, create, extract, modify, or convert Apple II disk images.

Primary sources used for this reference:

- AppleCommander repository: `https://github.com/AppleCommander/AppleCommander`
- AppleCommander site: `https://applecommander.github.io/`
- `a2kit` repository: `https://github.com/dfgordon/a2kit`

## Tool choice

Prefer `a2kit` for structured, scriptable workflows and broad format coverage.

Prefer AppleCommander for common image listing, extraction, import, and simple image creation tasks when its CLI is available.

On the machine used to author this skill:

- `a2kit` was installed at `/home/iolo/.cargo/bin/a2kit`
- AppleCommander CLI was available as `ac` at `/home/iolo/.local/bin/ac`
- `java` was present at `/usr/bin/java`

Do not assume all three are present on future machines. Verify first.

## What `a2kit` supports

According to the official README, `a2kit` emphasizes Apple II disk images, filesystems, and languages.

The README lists disk image support for:

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

The README also lists Apple DOS 3.2, Apple DOS 3.3, ProDOS, CP/M, and UCSD Pascal filesystem support.

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

## Common `a2kit` workflows

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

Tokenize Applesoft text:

```sh
a2kit tokenize -a 2049 -t atxt < hello.bas > hello.atok
```

Detokenize Applesoft from an image:

```sh
a2kit get -d demo.dsk -f HELLO -t atok | a2kit detokenize -t atok
```

Use `a2kit` first when the task needs repeatable scripting or format conversion.

## Common AppleCommander workflows

The local CLI help identified AppleCommander command `ac` with these practical operations:

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

Use AppleCommander when the workflow is straightforward and the CLI is already available.

## Practical cautions

- Back up important images before mutating them.
- Determine whether the image is DOS 3.3, ProDOS, Pascal, or another layout before assuming filename rules or file types.
- Distinguish tokenized AppleSoft files from plain text listings.
- Prefer JSON or machine-readable catalog output when a later step will parse results.
- After writes, recatalog the image and, if relevant, mount it in an emulator to confirm bootability or file visibility.
