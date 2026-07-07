# 6502 Opcode Table

## Agent Navigation

Use this guide when exact 6502 opcode bytes, addressing-mode availability, or cycle counts matter.

- For normal assembly writing and debugging, start with `6502.md`.
- For exact opcode bytes or timing, inspect `6502-opcodes.json`.
- For Apple II firmware calls, soft switches, or memory addresses, use `a2-peek-poke-call.md` and `a2-peek-poke-call.json`.
- Do not read the full JSON table unless the task requires instruction-level lookup.

## Data File

`6502-opcodes.json` contains:

- `opcodes`: instruction metadata with mnemonic, title, affected flags, and opcode bytes by addressing mode
- `timing`: cycle counts by mnemonic and addressing mode

Addressing mode keys:

- `Im`: immediate
- `Z`: zero page
- `Zx`: zero page,X
- `Zy`: zero page,Y
- `Ab`: absolute
- `Ax`: absolute,X
- `Ay`: absolute,Y
- `Ix`: indexed indirect, `(zp,X)`
- `Iy`: indirect indexed, `(zp),Y`
- `In`: indirect
- `Lb`: relative branch
- `A`: accumulator
- `Ip`: implied

Timing values ending in `+` indicate an additional cycle may apply, usually for page crossing or branch behavior.

## Lookup Pattern

1. Search `6502-opcodes.json` for `"name": "LDA"` or the target mnemonic.
2. Inspect the `hex` object for supported addressing modes and opcode bytes.
3. Inspect `timing` with the same mnemonic and addressing-mode key.
4. Cross-check with `6502.md` when flag or addressing behavior matters.
