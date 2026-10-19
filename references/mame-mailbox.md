# Mailbox sessions, profiles, and receipts

## Launch an owned session

From the skill directory (keep the launcher process handle):

```sh
python3 scripts/launch.py --transport mailbox --driver apple2 \
  --rompath /absolute/roms --output-dir /absolute/new-session \
  --headless --fast --timeout 180
```

The launcher remains as supervisor, while MAME's stdin is disconnected. Use the
host's process tool to keep this command running; it is not a detached service.
The mailbox implies `--debug`; headless defaults to the Qt debugger with SDL
and Qt offscreen settings. A Qt-enabled build is required. The `none` debugger
backend does not reliably hold stops in 0.285. Visible sessions use the platform
default debugger unless `--debugger` is supplied. `--visible` is the default;
`--headless` suppresses display/audio. `--throttle` is the default; `--fast`
disables throttle independently of visibility.

`--startup /absolute/adapter.lua` runs once after machine/CPU/debugger creation,
even at the initial debugger stop. It has globals `a2` and `a2_automation`.
Legacy `--script` is an autoboot script: it needs emulation to advance and is not
an equivalent startup mechanism. Do not combine the two. A startup error writes
`ready.json` with `ok:false` and disables command execution until a fresh session.

MAME console/json plugins are discovered portably, or supplied with
`--pluginspath`. The bundled `a2_mailbox` plugin is added to that search path.
The launcher sets `A2_MAME_SESSION`, `A2_MAME_SCRIPTS`, and optional
`A2_MAME_STARTUP`; no installed-skill path or game resources are embedded.

## Machine and media profiles

| Profile | Configuration | Media |
| --- | --- | --- |
| `floppy` (default) | Chosen `--driver`, default `apple2` | `--disk` copy on `-flop1` |
| `iie-cffa` | `apple2e -aux ext80 -ramsize 64K -sl7 cffa202` | `--disk` copy on `-hard1` |

For an unenhanced IIe with 64K main plus 64K auxiliary RAM:

```sh
python3 scripts/launch.py --transport mailbox --profile iie-cffa \
  --rompath /absolute/roms --cffa-rom /absolute/cffa20ee02.bin \
  --disk /absolute/disk.po --output-dir /absolute/new-cffa-session \
  --visible --throttle --timeout 180
```

Supply local 6502 CFFA firmware, or place the audited `a2cffa02` ROM set in
`--rompath`. Both machine and card are audited. Inspect slots *after* selecting
the controller (`mame apple2e -aux ext80 -sl7 cffa202 -listmedia`), then verify
`a2.devices()` after launch. An 800K raw ProDOS `.po` copied to `.hdv` is still the
same bytes; the extension selects the accepted hard-disk media path, not a format
conversion or a rule for every `.po` file. Other media layouts need separate
profiles and tests; do not force them through `-flop1`.

Configuration is ignored by default. `--read-config` explicitly enables it.
`--bgfx-chain CHAIN` enables visible BGFX shaders; `--avi recording.avi` records
inside the session directory. Both are opt-in. Preserve existing project/user
viewing settings when adapting their launcher; do not replace them with a
recorded benchmark's flags. `session.json` records this launch's actual command.

## Requests and recovery

From another host command, using the same session directory:

```sh
python3 scripts/rpc.py --session /absolute/new-session --call status
python3 scripts/rpc.py --session /absolute/new-session --call read --args '[2048,16]'
python3 scripts/rpc.py --session /absolute/new-session --lua 'return a2.devices()'
python3 scripts/rpc.py --session /absolute/new-session --call exit
```

The client takes an exclusive `client.lock`, atomically publishes `request.json`,
and waits for its unique `<id>.response.json`. The plugin archives the exact
`<id>.request.json` before executing under `pcall`. Lua syntax/runtime failures
produce receipts without disabling the transport. Serialization failure can
occur **after effects**; its error receipt says so. A malformed protocol or
transport I/O failure is terminal. `ready.json` only proves startup; a fresh
request proves liveness. The plugin uses a host-periodic callback, which runs
while ordinarily paused and while stopped in the debugger in tested 0.285.

An operation receipt is not necessarily a completed outcome: `go`, `save`,
`restore`, `reset`, and `exit` schedule work. Poll state/artifacts with a host
deadline; wait for process exit before reading saved media. Do not auto-retry a
mutation after timeout. Inspect the pending request, its accepted archive, and
matching response. The client refuses a pending request or an accepted request
without a response. A stale lock requires establishing that its client is dead;
never delete a live client's lock. Starting a fresh owned session is the simplest
recovery from an ambiguous or terminal session.

`--lua` intentionally executes local code with MAME's privileges. Use a private
owner-only session directory and an owned process; this is not a remotely exposed
service. POSIX creation uses mode 0700; on Windows use a directory whose ACL is
private to the user. No network, authentication, or concurrent-controller support
is claimed. The host lock does not serialize against autonomous Lua; stop the
controller first (`--call stop_automation`) before independent execution.

## Artifacts and checks

- `session.json`: exact command, child PID, profile, input/helper SHA-256 hashes,
  original/copy media paths. Startup version/driver are in `mailbox/ready.json`.
- `mailbox/<id>.request.json` and `.response.json`: accepted input and operation
  receipt. Keep both when reporting failures.
- `mame.log`: mailbox-session diagnostics; console sessions retain their terminal.
- `exit.json`: host elapsed time, exit reason/code, final copied-media hash and
  source unchanged check. Missing exit evidence means cleanup was not verified.
- Adapter result: explicit success/failure, native terminal state, progress, host
  and emulated time. A clean MAME exit does not establish adapter success.

Verify the source against the hash recorded at launch. If it already differed
from an old build manifest, report that separately. For saves, verify intended
file contents and permitted differences; a file written and later cleared can
finish byte-identical to its starting state.

Run `python3 scripts/smoke_mailbox.py --rompath /absolute/roms --output-dir /absolute/new-test`
for retained evidence. Add `--profile iie-cffa --cffa-rom ... --disk ...` to check
that configuration and source integrity. The raw smoke fixture verifies control,
not a particular operating system or game's full boot/completion. Use the
program's own adapter and outcome checks for that integration evidence.

The extracted design came from a Linux MAME 0.285 Carmen integration; it is not
proof of other MAME versions, hosts, drivers, concurrent controllers, or save-state
interchange. Test those separately. See [MAME plugin documentation](https://docs.mamedev.org/plugins/index.html).

Local validation on 2026-10-19 used Linux MAME 0.285: the existing original-Apple-II
console smoke (including floppy mount/eject and save/restore) passed; mailbox
smokes passed for `apple2` and `iie-cffa`, including reset/load invalidation,
watchdog, terminal startup failure, and clean exit without stdin. A separate
copied Carmen ProDOS image boot reached its rendered intro through CFFA; its
source hash remained unchanged. This validates that profile's boot, not a new
full-game autoplay run. Offline client/profile tests are included in the
cross-platform CI matrix; GUI/runtime support still requires local evidence.
