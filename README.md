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

The root `assets/` directory contains optional local tools and base disk images;
it is not included when a focused skill is installed. Resolve tools from an
explicit path, a compatible skill-local bundle, then PATH. Recipes accept
explicit base-image paths and work on copies.

## Skills

- `a2-basic`: AppleSoft BASIC, Integer BASIC, BASIC debugging, DOS/ProDOS BASIC workflows, and PEEK/POKE/CALL usage
- `a2-cc65`: Apple II native code with `cc65`, `ca65`, `cl65`, C, 6502 assembly, mixed C/assembly, raw binaries, firmware calls, and soft switches
- `a2-a2kit`: default scriptable Apple II disk-image inspection, creation, conversion, extraction, and modification with `a2kit`
- `a2-applecommander`: AppleCommander-specific disk-image workflows when requested or when `a2kit` is unavailable
- `a2-apple2ts`: configured `apple2ts-server` MCP sessions, uploads, input, screenshots, and debugging; HTTP compatibility guidance
- `a2-mame`: MAME Apple II/IIe control through a persistent Lua console, reusable helpers, and optional runtime tests
- `a2-hardware`: Apple II family hardware, firmware, ROM, memory map, slots, and model differences

## Development recipes

| Task | Start here |
| --- | --- |
| Build BASIC, C, standalone assembly, or mixed C/assembly | [Development recipes](references/development-recipes.md) |
| Package and verify a DOS/ProDOS disk | [a2kit skill](a2-a2kit/SKILL.md) |
| Run/debug with configured Apple2TS MCP | [MCP reference](references/apple2ts-mcp.md) |
| Run/debug with MAME Lua | [MAME reference](references/mame-lua.md) |

Honor an explicit emulator choice. Otherwise prefer configured Apple2TS MCP;
MAME is an independent alternative or side-by-side comparison target. Match
machine/ROM assumptions when comparing results. Neither emulator is required
to build or package the examples.

## Verification

```sh
python3 scripts/check.py
python3 scripts/test_workflows.py
```

The first check uses Python 3 only and checks materialized installed skills.
The second requires cc65 and a2kit, builds native fixtures, round-trips BASIC,
and packages all four fixtures on DOS/ProDOS copies. AppleCommander verification
is optional. CI pins cc65/a2kit; no emulator or ROM downloads are performed.

Optional emulator checks:

```sh
python3 a2-mame/scripts/smoke.py --rompath /absolute/roms --driver apple2
python3 a2-mame/scripts/smoke.py --rompath /absolute/roms --driver apple2e
```

MAME checks require a POSIX terminal and a build with console/json plugins and
Qt debugger support (offscreen for headless tests). Exit 77 means skipped for
missing prerequisites, not passed. Add `--disk /absolute/disk.dsk` for a copied
media mount/eject check. For Apple2TS, follow the
[MCP integration scenarios](references/apple2ts-integration.md) using the
configured MCP. Report PASS/FAIL/SKIP separately from offline checks.

## Later work

- Add a separate `a2-games` skill for input, graphics, animation, sound, and playable examples after the core development workflows.
- Rebuild asset download/setup scripts for `a2kit`, AppleCommander, ProDOS images, and other helper tools once the expected agent-skills `assets/` layout is settled.
