# IIe HGR verification with GSSquared

Use this recipe for standard AppleSoft HGR animation on an enhanced IIe (or
IIe with the same mapping). It does not cover II/II+, IIgs SHR, DHGR, auxiliary
HGR, or raster effects. Use the bounded client and handshake from
[native control](gssquared-control.md). All snippets below use that connected
client `c` and a selected session the task is authorized to control.

## Read status bits and poll text safely

IIe `$C01A`–`$C01D` expose TEXT, MIXED, PAGE2, and HIRES in **bit 7**.
Lower bits can reflect floating-bus data; exact comparisons with `0x00` or
`0x80` are incorrect. These reads inspect status; unlike `$C050`–`$C057`,
they do not select a video mode. They are not II/II+ status registers.

```python
from gs2debug import MEM_MAIN, VIDEO_MODE_TEXT40, ProtocolError

def iie_video_status(c):
    if c.get_status().platform_id not in (2, 3):
        raise ValueError("this helper expects an IIe or enhanced IIe")
    values = c.read_mem(MEM_MAIN, 0xC01A, 4)
    return dict(zip(("text", "mixed", "page2", "hires"),
                    (bool(value & 0x80) for value in values)))

def visible_text_lines(c):
    if not iie_video_status(c)["text"]:
        return None
    try:
        return c.video_text().as_lines()
    except ProtocolError as error:
        # A running guest can enter graphics between status and snapshot.
        if error.code == 6 and error.message == "current mode is not text":
            return None
        raise

# Text RAM is inspectable even when HGR is visible. This is not a screen capture:
text_ram_lines = c.video_text(page=1, mode=VIDEO_MODE_TEXT40).as_lines()
```

Bound the host polling deadline when waiting for a return to text. TEXT=false
with MIXED=true still means a graphics display with a text footer; it does not
make current-mode `video_text()` a visible-screen snapshot.

## Wait for a completed frame, then read visible HGR RAM

Launch once with a unique socket and a **copy** of a bootable application disk,
for example `-p 3 -s --debug <socket> --no-quit-confirm -ds6d1=<copy>`.
If the disk auto-runs HELLO, observe its startup. Otherwise wait for the BASIC
prompt, issue the appropriate RUN, and observe program readiness.

Identify the application's actual frame boundary from its code. This example
assumes it finishes drawing the hidden page, then **writes** `$C054` (page 1)
or `$C055` (page 2) to display it, with 80STORE/80COL off and standard main-RAM
HGR. If the program uses BIT/PEEK instead, select read access. A page-switch
access is a completed frame only when the application's drawing order makes
it one. Filter startup/blank snapshots rather than treating mode entry as
readiness. Programs without such a boundary can publish a readiness/completion
marker in RAM instead.

The following function collects nonblank frames at matching IO stops. It
registers the handler before commands, captures stops that precede replies,
accepts breakpoint mode 1, and leaves the machine **stopped** for inspection or
input setup. It clears its own breakpoint IDs and restores the handler it was
given; pass an existing handler as `previous_handler` if one is installed.

```python
from collections import deque
import struct
import time
from gs2debug import (BP_KIND_IO, BP_ACCESS_W, EVT_STOPPED, STOP_BP_IO,
                      MEM_MAIN_RAW)

def capture_hgr_frames(c, count=3, timeout=30.0, previous_handler=None):
    if count < 1 or timeout <= 0:
        raise ValueError("positive count and timeout required")
    pending, owned, frames = deque(), [], []
    deadline = time.monotonic() + timeout

    def collect(event_id, seq, data):
        if event_id == EVT_STOPPED:
            pending.append(data)
        if previous_handler is not None:
            previous_handler(event_id, seq, data)

    c.on_event(collect)
    try:
        for address in (0xC054, 0xC055):
            owned.append(c.bp_set(kind=BP_KIND_IO, address=address,
                                  access=BP_ACCESS_W))
        while len(frames) < count:
            pending.clear()  # discard stops from the preceding run
            c.continue_()
            while True:
                if time.monotonic() >= deadline:
                    raise TimeoutError("completed HGR frame did not arrive")
                if not pending:
                    c.wait_event(timeout=deadline - time.monotonic())
                    continue
                event = pending.popleft()
                reason, bp_id = struct.unpack_from("<II", event)
                if reason == STOP_BP_IO and bp_id in owned:
                    break
                # Another stop cannot progress to our frame without a policy
                # decision. Preserve it instead of blindly continuing.
                raise RuntimeError("unexpected stop; inspect before resuming")

            mode = c.get_status().execution_mode
            assert mode in (1, 2)  # matching event establishes this stop
            regs = c.get_regs()
            assert regs[15:28] == c.get_regs()[15:28]  # stable PB/PC/registers
            state = iie_video_status(c)
            if state["text"] or not state["hires"]:
                continue
            assert not (c.read_mem(MEM_MAIN, 0xC018, 1)[0] & 0x80), "80STORE on"
            assert not (c.read_mem(MEM_MAIN, 0xC01F, 1)[0] & 0x80), "80COL on"
            page = 2 if state["page2"] else 1
            ram = c.read_mem(MEM_MAIN_RAW, 0x4000 if page == 2 else 0x2000, 8192)
            # Canonical scanlines: ignore HGR holes and bit-7 color phase.
            height = 160 if state["mixed"] else 192
            pixels = bytearray()
            for y in range(height):
                offset = (y & 7)*0x400 + ((y >> 3) & 7)*0x80 + (y >> 6)*0x28
                pixels.extend(value & 0x7F for value in ram[offset:offset+40])
            if any(pixels):
                frames.append(dict(page=page, mode=mode, pixels=bytes(pixels),
                                   ram=ram, registers=regs))
        return frames
    finally:
        try:
            for bp_id in owned:
                c.bp_clear(bp_id)
        finally:
            c.on_event(previous_handler)

frames = capture_hgr_frames(c, count=6)
assert len({frame["pixels"] for frame in frames}) > 1  # animation changed
# Assert alternating pages only if the program promises double buffering.
assert all(a["page"] != b["page"] for a, b in zip(frames, frames[1:]))
```

For page-switch stops, an additional `pause()` is unnecessary: the captured
matching IO event already establishes a stable stop even when mode is 1.
Calling PAUSE deliberately changes that to mode 2 and emits another stop event.
If another controller is required, disconnect this one first; keep the owned
emulator alive and inspect its state on the next handshake.

## Input after readiness and restart checks

After a known completed frame and startup strobe clearing, inject the quit key
while stopped, then resume (for an ASCII-polled AppleSoft application,
`c.paste_text("Q")` followed by `c.continue_()`). Poll for the expected text
message with `visible_text_lines(c)` under a deadline. Use physical key events
instead when the application depends on key-down/up semantics. A mode change
at the beginning of HGR/HGR2 does not prove that initialization or `$C010`
clearing is finished and can lead to lost input.

Verify RUN restarts by collecting another nonblank completed frame, not by
sleeping for a fixed interval or merely observing TEXT=false. For this recipe,
clear owned frame breakpoints before quit/text polling so the checker does not
stop the application before it polls the key. Resume only when the task's
session lifecycle requires it; `capture_hgr_frames()` leaves a successful
capture stopped. On failure, inspect state before resuming. Use protocol QUIT
and wait for exit when the disposable owned test is finished.

Framebuffer changes verify guest drawing. A monochrome image decoded from
this RAM must be described as a RAM rendering, not a native GSSquared screenshot;
it does not verify artifact colors, CRT output, or rendered timing.

## Evidence and limits

These corrections follow a real enhanced-IIe AppleSoft double-buffered cube
task reported on 2026-10-06, checked against the local GSSquared sources
(`src/debugger/DebugProtocolServer.cpp` and IIe video-status handlers).
The snippets were then run against a copied cube disk using the installed
`~/.local/bin/GSSquared`: six distinct nonblank frames alternated pages
2/1/2/1/2/1, with mode 1 at each IO stop. Graphics-aware text polling, Q returning
to text, RUN restarting to a nonblank completed frame, and owned shutdown
with exit 0 all passed. No fixed application-startup delay was used.
The recipe assumes standard main-memory HGR and an application whose writes
mark completed frames; use a different event/marker for other drawing models.
