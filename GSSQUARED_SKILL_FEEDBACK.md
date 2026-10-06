# Feedback for the a2-gssquared skill developer

Date: 2026-10-06
From: Codex, following a real AppleSoft graphics task in apple2-with-ai

## Overall assessment

The skill was useful and sufficient to complete the task with native GSSquared. Its strongest features are concrete installation paths, the upstream gs2debug client, bounded requests, event capture before commands, explicit memory domains, copied media, and owned-process cleanup. I would use it again.

The task was to write and verify a rotating 3D wireframe cube in AppleSoft HGR mode. The final program uses perspective projection and both HGR pages. Source verification and disk packaging used a2kit; runtime verification used GSSquared throughout.

## Confirmed results

- Executable: /home/iolo/.local/bin/GSSquared, with installed assets.
- Client: /home/iolo/workspace/retro/gssquared/clients/python/src/gs2debug.
- Owned enhanced-IIe instance: -p 3 -s --debug <unique socket> --no-quit-confirm.
- A copied bootable DOS 3.3 disk mounted through -ds6d1= booted and automatically ran HELLO.
- hello() reported protocol version 1; get_status() confirmed platform_id 3.
- IO write breakpoints at $C054 and $C055 stopped at completed frame display switches.
- Six distinct completed frames alternated between pages 2, 1, 2, 1, 2, 1.
- Q returned to text mode. RUN restarted successfully, with a nonempty visible HGR frame verified after startup.
- Owned breakpoints were cleared; quit() closed the emulator and the process exited successfully.

Artifacts in /home/iolo/workspace/retro/apple2-with-ai: cube.bas, cube.dsk, cube.png. cube.png is a monochrome rendering decoded from guest HGR RAM, not a native emulator screenshot. The final temporary verification report was /tmp/cube-gs2-b5ebjg_8/result.json; temporary files are not durable references.

## Friction and suggested improvements

These failures were in my verification harness, not in the cube program. Better cookbook examples would have prevented several reruns.

1. **Distinguish a breakpoint stop from an explicit pause.** After pause() and STOP_PAUSE, execution_mode was 2. After an IO breakpoint and its matching STOP_BP_IO event, execution_mode was 1. My first checker incorrectly required 2 at both stops. The reference already warns that mode 1 alone does not prove completion; please add a concrete example explaining that a captured matching breakpoint event establishes the stop even when the mode is 1. An optional stable register readback would strengthen the example.

2. **Mask video-status bit 7.** For IIe $C01A-$C01D, compare byte & 0x80 rather than requiring the whole byte to equal 0x00 or 0x80. My exact-byte comparison timed out although the restarted program was running. The lower bits should not be used to decide the video mode. A tiny status helper covering text, mixed, page 2, and hires would be useful.

3. **Make text polling graphics-aware.** video_text() in current-mode selection raises ProtocolError code 6, "current mode is not text", during HGR. My initial Q-to-quit polling hit this. Show either a video-status guard before a current-mode text snapshot, or explicit video_text(page=1, mode=VIDEO_MODE_TEXT40) for examining text RAM. Keep the distinction between text RAM and the visible display clear.

4. **Wait for application readiness before sending keys.** A transition to graphics mode can happen early in HGR2/HGR initialization, before clearing both pages and the keyboard strobe. Sending Q as soon as graphics appeared could lose the key when the program subsequently cleared $C010. Prefer a completed-frame breakpoint or a program readiness marker. The successful checker verified the restarted visible frame after allowing startup to finish; a future recipe should use an event or marker instead of that fixed delay.

5. **Add a small HGR verification recipe.** A reusable example could boot HELLO, observe a completed page flip, pause, read the visible page in MEM_MAIN_RAW, compare successive frames, and clean up. IO breakpoint events plus framebuffer readback made real animation verification possible without assuming a screenshot socket API. Native screenshot capture can remain a separate documented workflow.

6. **Explain narrowly scoped sandbox launch permissions.** In this environment, launching native GSSquared required escalation because it opens a GUI. Iterating the checker led to repeated launch approval requests. A documented persistent-session controller pattern could reduce that friction while preserving bounded operations, unique sockets, copied media, and reliable final cleanup.

## Existing guidance worth retaining

The warnings about only one client, lost stop events if handlers are registered late, 0-based protocol drives versus 1-based CLI drives, physical versus mapped memory, and quit() discarding dirty media were all useful. The note that a scratch working directory does not isolate Documents output was accurate: shutdown logged a write to /home/iolo/Documents/gssquared-trace.bin.

I did not test IIgs operation, an MCP sidecar, native screenshots, media-save persistence, or the bundled smoke.py directly. This feedback is limited to the enhanced-IIe Python-client workflow exercised here.
