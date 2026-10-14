---
name: a2-gssquared
description: Control and debug native GSSquared Apple II and IIgs emulators through the gs2debug Python client or a configured MCP sidecar. Use for machine launch, disk mounting, keyboard input, text snapshots, CPU and memory inspection, stepping, breakpoints, and watchpoints.
---

# A2 GSSquared

For Windows/macOS setup, shell syntax, and emulator limitations, read
[references/host-platforms.md](references/host-platforms.md) when needed.

Honor the selected emulator and machine. Use a configured GSSquared MCP sidecar
when available; discover its actual tools and socket target. Otherwise use the
upstream `gs2debug` Python client with the native `--debug PATH` socket. Read
[references/gssquared-control.md](references/gssquared-control.md) before launch
or control; it covers setup, API examples, events, memory domains, and media.
For IIe HGR animation, graphics-aware polling, and application input readiness,
read [references/gssquared-graphics.md](references/gssquared-graphics.md).

## Workflow

1. Identify the executable, its assets, Python client, and requested platform.
   Prefer an explicit path, then PATH. Typical user installations put the binary
   in `~/.local/bin/GSSquared` and assets in `~/.local/share/GSSquared` on Linux;
   see the host reference for macOS bundles and Windows executables/client limits.
2. Attach only to the selected socket, or launch an owned process with a unique
   socket path. Keep emulator and controller in separate process groups. Use
   copied writable disks and configs; preserve existing sessions.
3. Handshake with `hello()` and confirm `get_status().platform_id`. Only one
   client may connect at a time; do not compete with an attached MCP sidecar.
4. Observe a pause/stop before stable CPU or memory setup. Choose mapped versus
   physical memory deliberately, particularly on IIgs. Use bounded requests and
   waits, and capture events before issuing commands that may emit them.
5. Verify guest results through stop events, register/memory readback, text, or
   visible graphics. A matching breakpoint event establishes a stop even when
   execution mode is 1. Wait for application readiness before sending input;
   a graphics-mode transition alone does not establish readiness.
6. Release held keys and clear only owned breakpoints. Disconnect an attached
   session; use `quit()` only for an owned process whose media may be discarded.

Protocol units are **0-based**, CLI/TOML drives **1-based**. `unmount()` discards
dirty data; `quit()` skips dirty-disk prompts. Preserve wanted writes through the
native save workflow before either operation. Full machine save states are not
shipped; device snapshots and `.gs2` configs are not full save states.

## Verification and companions

Run [scripts/smoke.py](scripts/smoke.py) for an owned scratch-process check of
handshake, memory, registers, execution breakpoints, stepping, text snapshots,
and shutdown; optionally test mount/unmount on a disk copy. See the reference
for arguments and prerequisites. Native rendering requires a usable display;
the script does not invent a headless flag. Offline packaging checks do not
prove emulator behavior.

- `a2-basic` writes BASIC; `a2-cc65` builds native programs; `a2-a2kit` packages
  disk images. AppleSingle/runtime programs need the appropriate guest loader.
- `a2-apple2ts` and `a2-mame` are independent alternatives. Match models, ROMs,
  and media copies for comparisons; do not silently move a user's session.
- The web build has no native debug socket. Use its UI when web control is
  explicitly requested, and account for media being lost on reload.
