# Windows, macOS, and Linux hosts

Read this when setting up tools or adapting shell commands. Apple II guest
addresses and disk formats are independent of the host OS; executable paths,
shell syntax, and emulator transports are not.

## Setup and tool discovery

Use Python 3.10 or newer. Examples use `python3` in macOS/Linux terminals and
`py -3` in Windows PowerShell. If those commands are absent, use the installed
Python 3 executable (`python` in many environments). Use `sys.executable` when
one Python script launches another.

| Tool | Windows | macOS | Linux |
| --- | --- | --- | --- |
| Python | Install Python 3; check `py -3 --version` | Install Python 3; check `python3 --version` | Check `python3 --version` |
| cc65 | Use the upstream Windows distribution; put its `bin` on PATH | Use an appropriate package or build upstream source | Use an appropriate package or build upstream source |
| a2kit | Use an upstream binary matching the host, or Cargo | Match Apple Silicon/Intel architecture, or use Cargo | Match the host architecture, or use Cargo |
| AppleCommander | Use a compatible native CLI or an explicitly configured CLI JAR with Java | Same; do not assume an `ac` wrapper exists | Same |
| Emulators | Install separately with required plugins/assets/ROMs | Resolve `.app` executable paths when necessary | Resolve installed executable and assets |

Upstream setup: [Python](https://www.python.org/downloads/),
[cc65](https://cc65.github.io/), [a2kit](https://github.com/dfgordon/a2kit),
[AppleCommander](https://applecommander.github.io/).
With a working Rust toolchain, `cargo install a2kit --version 4.4.2 --locked`
installs the version used by these disk recipes. Source builds may need the
host's compiler/linker prerequisites. The skills do not install tools automatically.

Prefer explicit executable arguments, then compatible skill-local bundles,
then PATH. Keep the cc65 distribution together: finding `cl65` alone is not
enough if its libraries, include files, or linker configs are missing.
Set `CC65_HOME` to that distribution root when needed. Quote paths with spaces.
For example, from the installed cc65 skill in PowerShell:

```powershell
$env:CC65_HOME = 'C:\Tools\cc65'
py -3 scripts/build_examples.py --cl65 'C:\Tools\cc65\bin\cl65.exe' --ca65 'C:\Tools\cc65\bin\ca65.exe' --ld65 'C:\Tools\cc65\bin\ld65.exe' --output-dir 'C:\a2-work\native'
```

The a2kit package helper also recognizes optional bundles at
`assets/tools/<os>-<arch>/a2kit` (`a2kit.exe` on Windows). OS names are
`linux`, `darwin`, `windows`; architecture names include `x86_64` and `arm64`.
AMD64 and aarch64 aliases are normalized. A directory name is a packaging
contract, not proof that an executable supports that architecture. No new
binaries are supplied by these skills; explicit paths and PATH remain usable.

## Shell and byte handling

Commands marked `sh` may use POSIX-only `<`, backslash line continuation, or
`NAME=value command`. Do not paste those forms into PowerShell unchanged.
Use single-line commands, `$env:NAME = 'value'`, and the Python helpers.
PowerShell invokes a quoted executable with `& 'C:\Tools\tool.exe' ...`.

For example, from the installed a2kit skill in PowerShell:

```powershell
py -3 scripts/package_disk.py --source 'C:\a2-work\hello.bas' --format basic --base-image 'C:\a2-work\dos33.dsk' --output-dir 'C:\a2-work\basic-disk' --name DEMOBAS
py -3 scripts/package_disk.py --source 'C:\a2-work\native\hello.as' --format applesingle --base-image 'C:\a2-work\prodos.po' --output-dir 'C:\a2-work\c-disk' --name DEMOC
```

Output directories must be new. Supply your own bootable base images.
Do not route disk images, tokenized BASIC, or machine code through text
pipelines. For a direct tool command without a helper, save and run a small
Python script; binary subprocess I/O works independently of shell versions:

```python
from pathlib import Path
import subprocess

result = subprocess.run(
    ['a2kit', 'tokenize', '-t', 'atxt', '-a', '2049'],
    input=Path('hello.bas').read_bytes(), capture_output=True,
    check=True, timeout=60,
)
Path('hello.atok').write_bytes(result.stdout)
```

For AppleCommander import, use the same binary input pattern with
`['ac', '-bas', 'demo.dsk', 'HELLO']`; for an explicitly supplied CLI JAR use
`['java', '-jar', '/path/to/cli.jar', '-bas', 'demo.dsk', 'HELLO']`.
Never put the entire Java command in an executable-path argument.

Use UTF-8 for host documentation/manifests and byte I/O for guest artifacts.
Preserve filename case even on case-insensitive filesystems. For an older
native tool that rejects Unicode filenames, copy inputs into a short ASCII
scratch directory and record their original paths and hashes.

## Emulator boundaries

- **Apple2TS:** discover configured MCP capabilities. Resolve uploads on the
  machine running the uploader; a Windows path is not a Linux/server path.
  Verify the local uploader on each host. Do not assume WSL and native Windows
  share executable paths, localhost behavior, or emulator sockets.
- **MAME:** supply `--pluginspath` when discovery fails. Visible launches use
  MAME's default debugger with `--debug`; `--debugger` selects a backend
  explicitly. The full smoke test still requires a POSIX PTY and a Qt-enabled
  build; native Windows reports SKIP (77). Manual Lua/startup-script use is
  separate from that smoke test. macOS also needs a compatible Qt build for
  the full smoke test; being POSIX is not sufficient.
- **GSSquared:** macOS bundles may use
  `GSSquared.app/Contents/MacOS/GSSquared`; Windows uses `GSSquared.exe`.
  Keep bundled assets with the application. The upstream Python client needs
  `socket.AF_UNIX`; Windows OS socket support alone does not establish Python
  client support. The smoke script probes this before launching and reports
  SKIP (77) if unavailable. A configured compatible MCP sidecar is another
  route. Use a short socket path; deep macOS temporary paths or Windows user
  directories may exceed the socket limit. A working display is required.

Check the actual environment's capabilities before promising runtime support.
CI package/build checks do not prove GUI, ROM, debugger, or socket behavior.
Report PASS, FAIL, and SKIP separately. See
[Python subprocess platform options](https://docs.python.org/3/library/subprocess.html)
and [socket availability](https://docs.python.org/3/library/socket.html#socket.AF_UNIX).
