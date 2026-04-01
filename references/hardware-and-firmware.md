# Apple II Hardware And Firmware

Use this reference for concise factual grounding when answering Apple II model, ROM, slot, memory, disk, and firmware questions.

## Model distinctions

### Apple II and Apple II+

- 6502-based 8-bit Apple II family machines with the original slot-oriented architecture.
- 40-column text is the default assumption.
- Integer BASIC and AppleSoft history differ across early configurations, so avoid assuming the same ROM set across all early machines.
- Many hardware discussions about language cards, Disk II, and ROM revisions start here.

### Apple IIe

- The practical baseline for many later Apple II workflows.
- Improved keyboard and firmware behavior compared with earlier machines.
- Frequently paired with 80-column/aux-memory expansion behavior and later productivity software.
- Distinguish standard IIe from enhanced IIe when firmware or instruction-level compatibility matters.

### Enhanced IIe

- Still a IIe, but firmware and CPU-related expectations can differ from the original IIe.
- Safer target when software assumes later IIe ROM behavior.
- If the emulator or hardware presents `APPLE2EE`, treat it as an enhanced IIe target.

## Slots and peripherals

- Apple II machines are highly slot-centric. Do not discuss storage, serial, mouse, or video add-ons without naming the card or slot assumption.
- Disk behavior depends on controller and DOS/ProDOS expectations, not just on the drive hardware.
- Mouse support is not universal; assume a card and appropriate firmware/software support are required.
- RamWorks or language-card style memory expansion changes what "available RAM" means.

## Firmware and ROM guidance

- ROM entry points and monitor behavior are model-specific enough that you should name the target machine when giving addresses or `CALL` examples.
- Soft switches are powerful but machine- and configuration-sensitive. Explain the side effect, not just the address.
- DOS 3.3, ProDOS, and bare ROM environments are materially different execution contexts.
- If a program depends on startup state, disk boot side effects, or firmware vectors, say so directly.

## Video and display assumptions

- Default to 40-column text unless the question clearly targets IIe 80-column support or a specific add-on.
- Low-resolution, high-resolution, mixed, and page-switching discussions should mention the relevant mode transitions and any soft-switch dependence.
- Do not imply graphics code is portable across all Apple II models without qualification.

## Memory guidance

- Zero page and page one are precious. Mention pressure on these areas for assembly routines.
- Auxiliary memory and expanded memory are not universally available.
- Language-card and bank-switching answers should specify the hardware assumption.

## Storage guidance

- Distinguish floppy vs hard-drive workflows.
- Distinguish image/container format from operating system format.
- When discussing bootability, say whether the user is talking about DOS 3.3, ProDOS, or raw monitor/bootstrap behavior.

## Answering style

Prefer answers in this format:

1. Name the likely or exact model.
2. State the relevant firmware or peripheral assumption.
3. Give the behavior or limitation.
4. Mention the main compatibility caveat.
