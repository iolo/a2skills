# Apple II Skills

Apple II agent skills split by task area.

## Install

With Node.js/npm installed, install all focused skills from GitHub with
Vercel's skills CLI (macOS/Linux):

```sh
npx skills add https://github.com/iolo/a2skills --full-depth --skill '*'
```

Windows PowerShell (use the `.cmd` launcher):

```powershell
npx.cmd skills add https://github.com/iolo/a2skills --full-depth --skill '*'
```

To preview available skills without installing (use `npx.cmd` on Windows):

```sh
npx skills add https://github.com/iolo/a2skills --full-depth --list
```

To install only selected skills:

```sh
npx skills add https://github.com/iolo/a2skills --full-depth --skill a2-basic a2-cc65 a2-apple2ts
```

Each focused skill is self-contained and includes its relevant reference files.

Each skill's `references/` contains regular files, so Windows clones and ZIP
downloads do not need symlink privileges. The canonical sources live in root
`references/`. After editing those sources, run
`python scripts/sync_references.py --write`; CI rejects stale copies.
To include a new reference in a skill, copy it into that skill's `references/`
directory and link it from `SKILL.md`. The sync script matches files by name.

The root `assets/` directory contains optional local tools and base disk images;
it is not included when a focused skill is installed. Resolve tools from an
explicit path, a compatible skill-local bundle, then PATH. Recipes accept
explicit base-image paths and work on copies.

## Windows and macOS setup

See [host platform setup](references/host-platforms.md) for tool prerequisites,
PowerShell examples, Intel/Apple Silicon tool selection, binary I/O, and
emulator limitations. Python helpers require Python 3.10 or newer. Use
`python3` on macOS/Linux, or `py -3` on Windows (`python` also works when it
selects the intended Python 3 installation). Install cc65 and a2kit separately
for build/disk workflows; a configured emulator is optional.

| Workflow | Linux | macOS | Native Windows |
| --- | --- | --- | --- |
| Skill package checks | CI configured | CI configured | CI configured; no symlinks needed |
| cc65/a2kit build and disk round trips | CI configured | CI configured | CI configured with native tools |
| Apple2TS MCP | Requires configured server/uploader | Requires configured server/uploader | Requires configured server/uploader |
| MAME console smoke test | POSIX PTY + Qt build + ROMs | POSIX PTY + Qt build + ROMs | SKIP; manual Lua/startup-script control remains available |
| MAME mailbox smoke test | No PTY; MAME 0.285 + Qt + ROMs validated | Runtime verification pending | Runtime verification pending |
| GSSquared smoke test | Requires client/socket/display/assets | Requires client/socket/display/assets | Requires AF_UNIX-capable Python/client/display/assets; otherwise SKIP |

The CI matrix is a verification mechanism, not a claim that every host or
emulator build has passed. Emulator runtime checks remain opt-in.

## Skills

- `a2-basic`: AppleSoft BASIC, Integer BASIC, BASIC debugging, DOS/ProDOS BASIC workflows, and PEEK/POKE/CALL usage
- `a2-cc65`: Apple II native code with `cc65`, `ca65`, `cl65`, C, 6502 assembly, mixed C/assembly, raw binaries, firmware calls, and soft switches
- `a2-disasm`: evidence-backed reverse engineering, loader and overlay analysis, mixed native/interpreted code, editable assets, gameplay mechanics, and reproducible disk reconstruction
- `a2-a2kit`: default scriptable Apple II disk-image inspection, creation, conversion, extraction, and modification with `a2kit`
- `a2-applecommander`: AppleCommander-specific disk-image workflows when requested or when `a2kit` is unavailable
- `a2-apple2ts`: configured `apple2ts-server` MCP sessions, uploads, input, screenshots, and debugging; HTTP compatibility guidance
- `a2-mame`: MAME Apple II/IIe control through a Lua console or local mailbox, bounded Lua automation, and copied floppy/CFFA media profiles
- `a2-gssquared`: native GSSquared Apple II/IIgs debug-socket control with the upstream Python client or a configured MCP sidecar
- `a2-hardware`: Apple II family hardware, firmware, ROM, memory map, slots, and model differences

## Development recipes

| Task | Start here |
| --- | --- |
| Build BASIC, C, standalone assembly, or mixed C/assembly | [Development recipes](references/development-recipes.md) |
| Recover source, assets, or mechanics from an existing program | [Disassembly skill](a2-disasm/SKILL.md) |
| Package and verify a DOS/ProDOS disk | [a2kit skill](a2-a2kit/SKILL.md) |
| Run/debug with configured Apple2TS MCP | [MCP reference](references/apple2ts-mcp.md) |
| Run/debug with MAME Lua | [MAME reference](references/mame-lua.md) |
| Automate MAME without stdin | [Mailbox and profiles](references/mame-mailbox.md), [Lua automation](references/mame-automation.md) |
| Run/debug with native GSSquared | [GSSquared reference](references/gssquared-control.md) |

Honor an explicit emulator choice. Otherwise prefer configured Apple2TS MCP;
MAME and GSSquared are independent alternatives or side-by-side comparison targets.
Match machine/ROM assumptions when comparing results. No emulator is required
to build or package the examples.

## Verification

```sh
python3 scripts/check.py
python3 scripts/test_portability.py
python3 scripts/test_mame.py
python3 scripts/test_workflows.py
```

Windows PowerShell:

```powershell
py -3 scripts/check.py
py -3 scripts/test_portability.py
py -3 scripts/test_mame.py
py -3 scripts/test_workflows.py
```

The first three checks use Python 3 only and check installed skills, host
portability, and mailbox failure/profile contracts. The fourth requires cc65 and a2kit, builds native fixtures,
round-trips BASIC, and packages all four fixtures on DOS/ProDOS copies. AppleCommander verification
is optional. CI pins cc65/a2kit; no emulator or ROM downloads are performed.

Optional emulator checks:

```sh
python3 a2-mame/scripts/smoke.py --rompath /absolute/roms --driver apple2
python3 a2-mame/scripts/smoke.py --rompath /absolute/roms --driver apple2e
python3 a2-mame/scripts/smoke_mailbox.py --rompath /absolute/roms --output-dir ./build/new-mailbox-test
```

The console smoke needs a POSIX terminal; the mailbox smoke does not use stdin.
Both need console/json plugins, ROMs, and Qt debugger support for headless tests. The launcher allows a
different debugger backend for visible sessions. Exit 77 means skipped for
missing prerequisites, not passed. Add `--disk /absolute/disk.dsk` for a copied
media mount/eject check. For Apple2TS, follow the
[MCP integration scenarios](references/apple2ts-integration.md) using the
configured MCP. Report PASS/FAIL/SKIP separately from offline checks.

For native GSSquared with its upstream Python client and a working display:

```sh
python3 a2-gssquared/scripts/smoke.py --client-src /absolute/gssquared/clients/python/src --platform 3 --output-dir ./build/gs2-iie-test
python3 a2-gssquared/scripts/smoke.py --client-src /absolute/gssquared/clients/python/src --platform 5 --output-dir ./build/gs2-gs-test
```

Use `--emulator /absolute/GSSquared` if it is not on PATH. Optional `--disk`
tests mount/unmount on a copy. See the [GSSquared reference](references/gssquared-control.md)
for prerequisites, media-discard behavior, and test coverage. These runtime tests
are optional; CI does not launch emulators or download their assets.

## Later work

- Add a separate `a2-games` skill for input, graphics, animation, sound, and playable examples after the core development workflows.
- Rebuild asset download/setup scripts for `a2kit`, AppleCommander, ProDOS images, and other helper tools once the expected agent-skills `assets/` layout is settled.
