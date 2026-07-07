# Apple II Skills

Apple II agent skills split by task area.

## Install

Install all focused skills from GitHub with Vercel's skills CLI:

```sh
npx skills add https://github.com/iolo/a2skills --full-depth --skill '*'
```

To preview available skills without installing:

```sh
npx skills add https://github.com/iolo/a2skills --full-depth --list
```

To install only selected skills:

```sh
npx skills add https://github.com/iolo/a2skills --full-depth --skill a2-basic a2-cc65 a2-apple2ts
```

Each focused skill is self-contained and includes its relevant reference files.

In this repository, each skill's `references/` files are symlinks to the canonical files in the root `references/` directory. The skills CLI dereferences those symlinks when copying skills, so installed skills get regular files.

The optional `assets/` directory can hold helper binaries such as `assets/a2kit`, `assets/ac`, or an AppleCommander jar for easier local setup. Skills should use bundled assets by direct path when present and executable.

## Skills

- `a2-basic`: AppleSoft BASIC, Integer BASIC, BASIC debugging, DOS/ProDOS BASIC workflows, and PEEK/POKE/CALL usage
- `a2-cc65`: Apple II native code with `cc65`, `ca65`, `cl65`, C, 6502 assembly, mixed C/assembly, raw binaries, firmware calls, and soft switches
- `a2-a2kit`: default scriptable Apple II disk-image inspection, creation, conversion, extraction, and modification with `a2kit`
- `a2-applecommander`: AppleCommander-specific disk-image workflows when requested or when `a2kit` is unavailable
- `a2-apple2ts`: `apple2ts` emulator control over its localhost HTTP API
- `a2-hardware`: Apple II family hardware, firmware, ROM, memory map, slots, and model differences

## TODO

- Expand `a2-cc65` with deeper workflows for linker configs, generated disk images, and emulator verification.
- Rebuild asset download/setup scripts for `a2kit`, AppleCommander, ProDOS images, and other helper tools once the expected agent-skills `assets/` layout is settled.
