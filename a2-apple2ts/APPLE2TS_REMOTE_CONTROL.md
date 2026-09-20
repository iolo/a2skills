# apple2ts Remote-Control Qualification

## Purpose

Qualify `apple2ts` breakpoint and keyboard automation before using it to collect
Rescue Raiders evidence. An HTTP `ok` response is not sufficient: every command
must produce an independently observable machine-state change.

This runbook is conditional. Static analysis is the primary method and proceeds
without apple2ts. Use this qualification only after `DISASSEMLY.md` records a
specific blocking ambiguity, exhausts static alternatives, and the user approves
the dynamic experiment.

`apple2ts` exposes no joystick input API. Joystick actions in Rescue Raiders are
manual user-assisted steps, not automation targets. Never simulate joystick
movement or buttons with PEEK/POKE, debugger memory writes, soft-switch writes,
or direct game-state mutation.

Rescue Raiders does expose two observed keyboard-controlled transitions suitable
for API automation after qualification: any key at `FLOW-20` and `S` during the
`FLOW-40` demo. Each is successful only when the expected next screen checkpoint
is observed; `accepted=true` alone is insufficient.

This is a disposable emulator exercise. Do not run it against a valuable dirty
session or treat its output as game evidence.

## Current Status

Status: **not qualified**.

Practice observation on 2026-07-14:

- `GET /api/machine` initially succeeded at `http://127.0.0.1:6502`, reporting
  `APPLE2EE`, `debugEnabled=true`, `runMode=running`, and a dirty mounted
  `rescue_raiders.woz` in `fd1`. The user had mounted the DSK; apple2ts converted
  it to an internal WOZ representation on the fly. The reported name does not
  identify the original mounted container, and the internal `dirty` flag does
  not prove that the source DSK was modified.
- `GET /api/drives` immediately disagreed and reported all drives unmounted.
- `GET /api/debug/cpu` returned zero for every register while the machine was
  reported running. Because the machine was not paused, this was not accepted as
  a valid CPU snapshot or treated alone as an API defect.
- Two existing memory-write breakpoints were visible, so deleting all
  breakpoints would have destroyed user debugger state.
- A memory read correctly refused to run while the machine was unpaused.
- The server became unreachable before save-state export. No reset, input,
  breakpoint mutation, media mutation, or save-state import was attempted.

Keyboard-path exercise observation later on 2026-07-14:

- Machine and drive preflight agreed that the DSK-derived internal WOZ was
  mounted, debug was enabled, and no breakpoints existed.
- `POST /api/machine/boot` returned `ok` with `runMode=booting`, but its response
  showed `fd1` unmounted.
- The API then remained unreachable for the complete bounded poll. No `Space`,
  `S`, joystick action, debugger write, or follow-up recovery endpoint was sent.
- Per user direction, this was classified as unexpected apple2ts behavior and
  investigation stopped. Do not repeat `/api/machine/boot` as a reboot method
  without asking the user first.

Conclusion: endpoint reachability and `{ "ok": true }` do not establish a
coherent remote-control session. The disassembly must not depend on this API
until the qualification below passes.

Operator rule: apple2ts is known to be fragile and is the available emulator for
this work. When it behaves unexpectedly or unreasonably, stop at the first
anomaly and ask the user what to do. Do not investigate by trying additional
endpoints, repeated resets, remounts, speculative recovery, or alternate control
sequences unless the user directs the next step.

## Required Environment

1. Start a dedicated browser session at
   `http://127.0.0.1:6502/?remoteControl=1&debug=on`.
2. Use a scratch session with no valuable mounted media or dirty drive state.
3. Pin the emulator revision, browser, machine model, ROM identity, and API base
   URL in the run log.
4. Record the operator-supplied source path and SHA-256 separately from the
   emulator's internal mounted-media filename.
5. Use only endpoints documented by the `apple2ts` OpenAPI specification. Do not
   guess endpoint names or request bodies.
6. Give every HTTP request a connection and total timeout. A timeout, malformed
   response, or contradictory endpoint state aborts the run.

## Practice Fixture

Use a tiny binary-block program at `$0800`, not Rescue Raiders. It polls the
keyboard latch, stores the last key at `$0300`, clears the strobe, increments a
counter at `$0301`, and loops:

```asm
        .org $0800
loop:   lda $C000
        bpl loop
key:    sta $0300
        bit $C010
        inc $0301
        jmp loop
```

Expected bytes:

```text
AD 00 C0 10 FB 8D 00 03 2C 10 C0 EE 01 03 4C 00 08
```

The stable breakpoint target is `$0805` (`2053` decimal), immediately after a
key is observed and before it is stored.

## Qualification Procedure

### 1. Preflight Consistency

- Read `GET /api/machine` twice with a short bounded delay.
- Read `GET /api/drives` and `GET /api/debug/breakpoints`.
- Require stable machine identity and run mode.
- Require drive state reported by machine and drive endpoints to agree.
- Inventory breakpoint IDs; never use `DELETE /api/debug/breakpoints` in a
  shared session.
- Abort if the server disappears or JSON envelopes are inconsistent.

### 2. Reversibility Check

- Export a save state with snapshots before the first mutation.
- Verify that the response contains nonempty base64 data and record its SHA-256.
- Pause the emulator, confirm `runMode=paused`, then record the initial machine,
  drives, CPU, memory `$0300-$0301`, and breakpoint set. CPU and memory reads
  taken while running are not qualification evidence.
- At the end, import that exact save state and require all recorded state to
  match. If import cannot restore the session, qualification fails.

Run this step only in the dedicated scratch session. Save-state support is not a
license to experiment on a dirty user session.

### 3. Fixture Load

- Pause and confirm `runMode=paused`.
- Load the fixture as `sourceType=binary-block`, `address=2048`, `autoRun=true`.
- Immediately request pause, wait for `runMode=paused`, and abort/ask the user if
  the resulting state is surprising.
- Re-read `$0800-$0810` and require exact fixture bytes.
- Initialize `$0300-$0301` to zero and verify the write.

### 4. Breakpoint Exercise

- Create exactly one breakpoint with `{ "address": 2053 }`.
- Capture the returned breakpoint ID and confirm it with the list endpoint.
- Resume, inject one `A` key, and poll machine state with a fixed deadline.
- Success requires `runMode=paused`, `PC=$0805`, and `A=$C1` (`'A' | $80`).
- Step or resume far enough to store the key, then require `$0300=$C1` and a
  one-count increment at `$0301`.
- Delete only the captured breakpoint ID and confirm that it is absent while all
  pre-existing breakpoint IDs remain.

Never infer a breakpoint hit merely because `resume` or breakpoint creation
returned `ok`.

### 5. Keyboard Exercise

Test the three input forms separately and verify each through fixture memory:

- `type=key`, key `A`, `release=true` must store `$C1`.
- `type=keyCode`, key code `13`, `release=true` must store `$8D`.
- `type=text`, text `AB` must advance the counter twice and finish with `$C2`.

Clear the keyboard strobe and reset the counter between cases. Bound every wait;
never use an unbounded sleep as synchronization. An `accepted=true` response
without the expected memory transition is a failure.

### 6. Restore and Repeat

- Import the pre-exercise save state.
- Re-read machine, drives, CPU, memory, and breakpoint IDs.
- Require exact restoration of all recorded invariants.
- Repeat the complete exercise three times from fresh dedicated browser sessions.

Qualification passes only after three consecutive clean runs. Save the JSON run
manifests and a concise Markdown summary under
`disasm/traces/apple2ts-qualification/`.

## Automation Rules

- Serialize mutating API calls. Do not issue reset, mount, resume, input, or
  breakpoint mutations in parallel.
- Poll an explicit state predicate after every mutation.
- Use bounded deadlines and log every request, response, and observation with a
  monotonic sequence number.
- Treat contradictory endpoint results as a hard failure, not a retryable
  warning.
- Treat any undocumented or surprising state transition as a user-escalation
  boundary. Preserve the last request/response and ask before doing anything
  else.
- Never delete all breakpoints. Delete only IDs created by the current run.
- Separate `type=text` command injection from precise game keypresses. Gameplay
  input must use `type=key` or `type=keyCode` and verify press/release semantics.
- Limit the keyboard API to actual keyboard-controlled actions. It is not a
  substitute for joystick axes or buttons.
- For the game, known keyboard automation includes any key at `FLOW-20` and `S`
  at `FLOW-40`. Verify arrival at `FLOW-30` and `FLOW-60` respectively rather
  than assuming input delivery succeeded.
- When a trace requires joystick input, first arm the breakpoint/watchpoint and
  verify the precondition, then ask the user for one precisely described action.
  Record the requested action, the user's completion signal, and the resulting
  observed state in the run manifest.
- Do not use PEEK/POKE, debugger memory writes, soft-switch writes, or patched
  game state to impersonate joystick input. Memory mutation is allowed only in
  a separately identified perturbation experiment, never as input evidence.
- Do not reuse save states across emulator revisions, ROMs, mounted-image hashes,
  or machine configurations.
- Do not infer the source container from an API-reported `.woz` name. apple2ts
  may convert a mounted DSK to WOZ internally; provenance comes from the original
  mount request and source hash.

## Abort and Fallback Policy

Abort without collecting evidence when:

- The API becomes unreachable.
- Machine and drive endpoints disagree.
- CPU or memory reads are invalid after a confirmed pause.
- A breakpoint fails to halt at the expected PC.
- Key input is accepted but produces no verified latch or memory transition.
- State restoration fails.

If qualification cannot pass, dynamic work is blocked. Perform a documented
manual capture with repeated user-assisted observations only when directed by
the user. Do not assume another emulator or control API is available. Static
guesses must not be promoted to runtime evidence to work around remote-control
failure.

## User-Assisted Joystick Protocol

For a joystick-dependent experiment:

1. State the exact initial screen/state and verify it without mutation.
2. Arm only the required trace targets.
3. Ask the user for one bounded action, such as "move fully right for about one
   second and release" or "press joystick button 0 once."
4. Wait for the user to report completion; do not approximate the action through
   another API.
5. Capture the postcondition and label timing or analog magnitude as
   user-controlled uncertainty.
6. Repeat when the conclusion depends on timing, axis magnitude, or button-edge
   behavior.

User-assisted joystick observations may confirm behavior, but exact timing or
analog thresholds require repeated traces or direct observation of the game's
joystick-reading routine.
