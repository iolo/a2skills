# AppleSoft BASIC Cheat Sheet

## Use This For

Use when writing or debugging AppleSoft BASIC for Apple II systems.
Prefer plain source listings unless tokenized output is explicitly requested.

## Default Rules

- Start line numbers at `10`, increment by `10`.
- Keep lines readable on 40-column displays.
- Prefer simple control flow over dense one-line tricks.
- Mention machine assumptions before using `PEEK`, `POKE`, `CALL`, firmware hooks, slots, or 80-column features.
- When output is meant for emulation or disk, give source first.

## Core Syntax Patterns

### Print text

```basic
10 PRINT "HELLO"
```

### Prompt for input

```basic
10 INPUT "NAME"; N$
20 PRINT "HELLO "; N$
```

### Menu key input

```basic
10 GET A$
20 IF A$ = "" THEN 10
```

### Loop

```basic
10 FOR I = 1 TO 10
20 PRINT I
30 NEXT I
```

### Branch

```basic
10 IF X = 0 THEN 100
```

### Subroutine

```basic
10 GOSUB 100
20 END
100 PRINT "DONE"
110 RETURN
```

## Common Gotchas

- `GET` reads one character and often needs a loop for empty input.
- `INPUT` and `READ` behave differently; do not substitute casually.
- String variables end with `$`.
- Arrays need `DIM` before use.
- Wrong line targets are a common failure mode.
- Dense use of `:` hurts readability and debugging.
- Hardware-dependent `PEEK`/`POKE` code must name the target machine.

## Use Carefully

- `PEEK`
- `POKE`
- `CALL`
- `ONERR`
- graphics and firmware entry points

When using them, say:

- target model
- relevant address or routine
- expected effect

## Debug Checklist

Check:

- bad line-number flow
- string vs numeric mistakes
- missing `DIM`
- broken `GOSUB` / `RETURN`
- machine-specific assumptions
- syntax around `IF`, separators, and function use
