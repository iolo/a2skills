# INTEGER BASIC Reference

## Agent Navigation

Use this file only when the task specifically involves Integer BASIC.

- For AppleSoft BASIC, use `applesoft.md`.
- For DOS 3.3 or ProDOS commands, use `appledos.md` or `prodos.md`.
- For `PEEK`, `POKE`, `CALL`, vectors, or soft switches, use `a2-peek-poke-call.md`.
- Integer BASIC differs from AppleSoft in variable types, string behavior, and available keywords; do not assume AppleSoft syntax applies.

## Practical Guidance

- State when you are assuming an Integer BASIC environment.
- Keep examples small and line-numbered.
- Avoid AppleSoft-only keywords unless explicitly discussing incompatibility.
- When disk behavior matters, name DOS 3.3, ProDOS, or another environment.

## Statements and Lines

A line typed without a line number is executed immediately;
those lines typed with a line number are saved for execution with the `RUN` command.

- `:` Separates multiple statements on the same line.
- `REM` Designates a remark for comments.

## Operations on Whole Programs

- `NEW` Erases the current program and clears all variables.
- `CLEAR` Resets all variables.
- `LIST` Displays the entire current program.
- `LIST n-m` Displays the lines from `n` to `m`.
- `RUN` Executes the current program.
- `RUN n` Executes the current program from line `n`.
- `RUN name` Executes the program `name` from disk.
- `LOAD name` Loads the program `name` from disk.
- `SAVE name` Saves the program on the disk as `name`.

## Variables

Where A is a letter, B is a letter or digit.

- Integer AB +/- 32767
- String AB$ 0 to 255 characters

## Arrays

- `DIM` Allocates space for an array or string.

##  Arithmetic Operators

- `=` Assigns a value to a variable
- `-` Subtraction
- `+` Addition
- `/` Division
- `*` Multiplication
- `^` Exponentiation

## Logical Operators

- `AND` Both true
- `OR` Either one or both true
- `NOT` Is false

## Relational Operators

- `=` Equal to
- `<` Less than
- `>` Greater than
- `<=` Less than or equal to
- `>=` Greater than or equal to
- `#` Not equal to

## Arithmetic Functions

- `ABS(x)` Absolute value of x
- `SGN(x)` -1 if x<0, 0 if x=0, 1 if x>0
- `RND(x)` Random number in the range 0 <= r < x

## String Operations

- `LEN(s)` Length of string s
- `ASC(s)` ASCII code for first character in string s

## Control

- `GOTO n` Branches to line n
- `IF cond THEN s1` Executes statement if expr is true
- `FOR v=x TO y STEP z` Begins a loop for all values of v from x to y by z; if step is omitted, 1 is understood.
- `NEXT v` Repeats loop for next value of v
- `GOSUB n` Branches to subroutine at line n
- `RETURN` Returns to point of call from a subroutine
- `POP` Removes one address from the return stack
- `STOP` Halts program and print line number
- `CON` Resumes program execution
- `END` Halts program execution

## Utility Statements

- `PEEK(addr)` Value of memory location addr
- `POKE addr,x` Sets memory location addr to x
- `CALL addr` Executes machine language routine at addr
- `HIMEM:addr` Sets highest available memory to addr
- `LOMEM:addr` Sets lowest available memory to addr.
- `TRACE` Displays the number of each executed line
- `NOTRACE` Turns line numbering off
- `DSP` v1,v2.. Displays v1,v2...each time they change.

## Graphics

- `GR` Sets lores graphics mode and clears screen
- `COLOR=x` Sets lores drawing color to x
- `PLOT x,y` Draws a dot at location x,y
- `HLIN x1,x2 at y` Draws a horizontal line from x1,y to x2,y
- `VLIN y1,y2 at x` Draws a vertical line from x,y1 to x,y2
- `SCRN(x,y)` The color of the dot at location x,y.

## Input/Output

- `IN# n` Re-directs input from slot n
- `INPUT s;x,y` Prompts with string s, then reads x,y.
- `PDL(n)` Value of paddle n, either 0 or 1
- `PR# n` Re-directs output to slot n
- `PRINT` x,y,... Prints strings or values
- `TEXT` Sets text mode
- `VTAB n` Sets vertical position to n

## Source

[Apple Computer, Apple II Reference Manual (January 1978)](https://www.applelogic.org/files/AIIREDBOOK.pdf), Integer BASIC functions.
