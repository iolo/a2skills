# Apple II PEEK, POKE, CALL, And Soft Switches

## Agent Navigation

Use this guide when a task involves Apple II memory addresses, firmware entry points, DOS vectors, soft switches, or BASIC `PEEK`, `POKE`, and `CALL` examples.

- For exact address lookup, inspect `a2-peek-poke-call.json`.
- For AppleSoft syntax around `PEEK`, `POKE`, or `CALL`, use `applesoft.md`.
- For model-specific hardware interpretation, use `hardware-and-firmware.md`.
- For 6502 instruction behavior, use `6502.md`.
- Always state machine, ROM, DOS, slot, and peripheral assumptions when an address is not universal.

## Data File

`a2-peek-poke-call.json` is a list of records. Each record has:

- `section`: broad group, such as low RAM, DOS 3.3 area, ROM soft switches, CALL entry points, or vectors
- `address_expr`: common decimal or signed BASIC address spelling
- `int16`: signed 16-bit value when useful for AppleSoft negative addresses
- `uint16`: unsigned 16-bit address
- `hex`: hexadecimal address
- `type`: `PEEK`, `POKE`, `PEEK/POKE`, `CALL`, or `SOFTSWITCH`
- `usage`: concise explanation

## Lookup Pattern

1. Search by `usage` term first, such as `keyboard`, `speaker`, `text mode`, `ONERR`, or `DOS`.
2. Use `hex` and `uint16` for assembly or debugger work.
3. Use `address_expr` or `int16` for AppleSoft examples.
4. Explain side effects before recommending `POKE`, `CALL`, or soft-switch access.
5. Prefer a documented firmware routine or DOS command when direct memory access is not necessary.

## Common Cautions

- Soft switches often trigger behavior on read or write; do not treat them as passive variables.
- DOS 3.3 and ProDOS have different assumptions. Do not reuse DOS vectors blindly.
- Slot firmware and peripheral cards can change behavior.
- Negative AppleSoft addresses are signed 16-bit aliases for high memory addresses.
