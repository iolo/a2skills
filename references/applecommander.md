# AppleCommander

Use this reference when the task needs straightforward Apple II disk-image listing, extraction, import, or simple image creation with AppleCommander.

## Installed tools on the authoring machine

The machine used to create this skill had:

- AppleCommander CLI as `ac` at `/home/iolo/.local/bin/ac`
- `java` at `/usr/bin/java`

Do not assume both are present on every future machine. Verify first.

## Best fit

Prefer AppleCommander when:

- the workflow is straightforward and interactive rather than highly scripted
- the local machine already has `ac` available
- the task is simple listing, extraction, import, or image creation
- conservative DOS 3.3 or ProDOS operations are enough

## High-value commands

The local CLI help identified these practical operations:

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
