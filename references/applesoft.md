# AppleSoft BASIC

## Agent Navigation

Use this file for AppleSoft BASIC syntax, idioms, debugging, and keyword lookup.

- Writing or fixing a program: read Practical Guidance first, then search Keyword Quick Reference only for specific statements or functions.
- Checking exact syntax: search for the keyword name in Keyword Quick Reference.
- Debugging flow or runtime behavior: read Practical Guidance > Debug Checklist, then inspect the relevant keyword.
- DOS 3.3 or ProDOS command details: prefer `appledos.md` or `prodos.md`; use the DOS quick reference here only for BASIC-facing reminders.
- PEEK, POKE, CALL, firmware vectors, and soft switches: prefer `a2-peek-poke-call.md`; inspect `a2-peek-poke-call.json` only for exact address lookup.
- Integer BASIC: use `integerbasic.md`, not this file.

## Contents

- Practical Guidance
- Canonical Examples
- Keyword Quick Reference
- Error Codes
- DOS 3.3 / ProDOS Quick Reference
- References

## Practical Guidance

### Use This For

Use when writing or debugging AppleSoft BASIC for Apple II systems. Prefer plain source listings unless tokenized output is explicitly requested.

### Default Rules

- Start line numbers at `10`, increment by `10`.
- Keep lines readable on 40-column displays.
- Prefer simple control flow over dense one-line tricks.
- Mention machine assumptions before using `PEEK`, `POKE`, `CALL`, firmware hooks, slots, or 80-column features.
- When output is meant for emulation or disk, give source first.

### Common Gotchas

- `GET` reads one character and often needs a loop for empty input.
- `INPUT` and `READ` behave differently; do not substitute casually.
- String variables end with `$`.
- Arrays need `DIM` before use.
- Wrong line targets are a common failure mode.
- Dense use of `:` hurts readability and debugging.
- Hardware-dependent `PEEK`/`POKE` code must name the target machine.

### Use Carefully

- `PEEK`
- `POKE`
- `CALL`
- `ONERR`
- graphics and firmware entry points

When using them, say:

- target model
- relevant address or routine
- expected effect

### Debug Checklist

Check:

- bad line-number flow
- string vs numeric mistakes
- missing `DIM`
- broken `GOSUB` / `RETURN`
- missing `RESTORE` before re-reading `DATA`
- `GET` loops that do not handle empty input
- dense `:` chains that hide branch targets
- machine-specific assumptions
- syntax around `IF`, separators, and function use

## Canonical Examples

### Print Text

```basic
10 PRINT "HELLO"
```

### Prompt For Input

```basic
10 INPUT "NAME"; N$
20 PRINT "HELLO "; N$
```

### Menu Key Input

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

### DATA Loop

```basic
10 READ A$
20 IF A$ = "END" THEN 50
30 PRINT A$
40 GOTO 10
50 END
100 DATA APPLE,II,END
```

## Keyword Quick Reference

This section is lookup-oriented. Search for the statement, function, or operator name rather than reading it start to finish.

### Statements

#### Variable Control

```
CLEAR
```
Clear all variables

```
[LET] *var* = *expr*
```
Assign variable

```
DIM *var*( *size* [, *size* ...] ) [, *var*( *size* [, *size* ...] ) ...]
```
Allocate array(s) with given dimension(s)

```
DEF FN *name*(*var*) = *aexpr*
```
Define function of a single variable

#### Flow Control

```
GOTO *linenum*
```
Jump to line number

```
GOSUB *linenum*
```
Enter subroutine at line number

```
RETURN
```
Return from subroutine

```
ON *aexpr* GOTO *linenum* [, *linenum* ...]
```
Branch based on index (value = 1, 2, ...)

```
ON *aexpr* GOSUB *linenum* [, *linenum* ...]
```
Subroutine branch based on index (value = 1, 2, ...)

```
POP
```
Convert last `GOSUB` into a `GOTO`

```
FOR *var* = *aexpr* TO *aexpr* [ STEP *aexpr* ]
```
Loop with counter variable

```
NEXT [*var* [, *var* ...] ]
```
End of loop(s)

```
IF *expr* THEN *statement*
IF *expr* GOTO *linenum*
```
Conditional; if *expr* is false, rest of line is skipped

```
END
```
Terminate program cleanly

```
STOP
```
Break, as if an error occurred

#### Error Handling

```
ONERR GOTO *linenum*
```
Set error hook

```
RESUME
```
Retry line that caused `ONERR GOTO`

#### Text Input/Output

```
PRINT *expr* [ [;,] *expr* ... ] [;]
```
Output text. `;` concatenates, `,` advances to next tab stop. A trailing `;` suppresses line break. *expr* can include `SPC(*aexpr*)` to advance by multiple spaces, or `TAB(*aexpr*)` to advance to column.

```
INPUT [*string* ;] *var* [, *var* ...]
```
Read line of comma-delimited input, with optional prompt

```
GET *var*
```
Read single key

```
HOME
```
Clear text display

```
HTAB *aexpr*
```
Position text cursor horizontally (1...40 or 1...80)

```
VTAB *aexpr*
```
Position text cursor vertically (1...24)

```
INVERSE
```
Set output mode to black-on-white

```
FLASH
```
Set output mode to flashing

```
NORMAL
```
Set output mode to white-on-black

```
TEXT
```
Set display to text mode

#### Lo-Res Graphics

```
GR
```
Set display to mixed test/low resolution ("lores") graphics mode, clear screen to black

```
COLOR= *aexpr*
```
Set lores color (0...15)

```
PLOT *aexpr*, *aexpr*
```
Plot lores point (x = 0...39, y = 0...39/47)

```
HLIN *aexpr*, *aexpr* AT *aexpr*
```
Plot horizontal line (x1, x2 at y)

```
VLIN *aexpr*, *aexpr* AT *aexpr*
```
Plot vertical line (y1, y2 at x)

#### Hi-Res Graphics

```
HGR
```
Set display to mixed/high resolution ("hires") graphics mode, clear screen to black

```
HGR2
```
Set display to full hires mode (page 2), clear screen to black

```
HPLOT [TO] *aexpr*, *aexpr* [ TO *aexpr*, *aexpr* ] ...
```
Plot hires point/line (x=0...279, y=0...191)

```
HCOLOR= *aexpr*
```
Set hires color (0...7)

#### Inline Data

```
DATA *value* [, *value* ...]
```
Define inline data. Values can be literals (unquoted strings), strings, or numbers

```
READ *var* [, *var* ...]
```
Read the next DATA value

```
RESTORE
```
Restore the DATA pointer to the first value

#### Miscellaneous

```
REM [*comment*]
```
Begin a comment; rest of line is skipped

```
TRACE
```
Turn on trace mode (line numbers printed)

```
NOTRACE
```
Turn off trace mode

#### Hi-Res Shape Tables

```
ROT= *aexpr*
```
Set hires shape table rotation (0...63)

```
SCALE= *aexpr*
```
Set hires shape table scale (1...255)

```
DRAW *aexpr* [ AT *aexpr*, *aexpr* ]
```
Draw hires shape table shape in color

```
XDRAW *aexpr* [ AT *aexpr*, *aexpr* ]
```
Draw hires shape table shape with XOR

#### Interpreter and Program State

```
CONT
```
Continue from a STOP

```
DEL
```
Delete lines of program

```
LIST [ *linenum* [, *linenum* ] ]
```
List lines of program

```
NEW
```
Clear program and variables

```
RUN [ *linenum* ]
```
Start program execution at line

#### Native Platform Interaction

```
HIMEM: *aexpr*
```
Set upper address of variable memory

```
LOMEM: *aexpr*
```
Set lower address of variable memory

```
WAIT *aexpr*, *aexpr* [, *aexpr*]
```
Wait until memory location masked by second argument equals third argument (or zero)

#### Cassette Tape

```
LOAD
```
Load program from cassette

```
RECALL
```
Load variables from cassette

```
SAVE
```
Save program to cassette

```
STORE
```
Save variables to cassette

```
SHLOAD
```
Load hires shape table from cassette

#### Compatibility Shims

```
SPEED= *aexpr*
```
Set character output delay — *has no effect*

```
POKE *aexpr*, *aexpr*
```
Set memory location to value

- `POKE 32,*n*` — Text window left edge
- `POKE 33,*n*` — Text window width
- `POKE 34,*n*` — Text window top edge
- `POKE 35,*n*` — Text window bottom
- `POKE 36,*n*` — Text cursor x
- `POKE 37,*n*` — Text cursor y
- `POKE 216,*n*` — ONERR flag (*n* < 128 disables ONERR handler)
- `POKE 230,*n*` — Hi-Res plotting page (32 = page 1, 64 = page 2)
- `POKE 49168,0` or `POKE -16368,0` — clear keyboard strobe
- `POKE 49200,0` or `POKE -16336,0` — toggle speaker (no-op)
- `POKE 49232,0` or `POKE -16304,0` — graphics mode
- `POKE 49233,0` or `POKE -16303,0` — text mode
- `POKE 49234,0` or `POKE -16302,0` — full graphics mode
- `POKE 49235,0` or `POKE -16301,0` — mixed text/graphics mode
- `POKE 49236,0` or `POKE -16300,0` — display page 1
- `POKE 49237,0` or `POKE -16299,0` — display page 2
- `POKE 49238,0` or `POKE -16298,0` — lores graphics mode
- `POKE 49239,0` or `POKE -16297,0` — hires graphics mode

```
CALL *aexpr*
```
Call native routine

- `CALL 54915` or `CALL -10621` — clear stack (pop all `FOR`/`NEXT`, `GOSUB`/`RETURN`, and `ONERR`/`RESUME` entries)
- `CALL 62248` or `CALL -3288` — pop `ONERR`/`RESUME` entry from stack
- `CALL 62436` or `CALL -3100` — reveal hi-res page 1
- `CALL 62450` or `CALL -3086` — clear current hi-res page to black
- `CALL 62454` or `CALL -3082` — clear current hi-res page to current color
- `CALL 64500` or `CALL -1036` — move cursor right
- `CALL 64528` or `CALL -1008` — move cursor left
- `CALL 64538` or `CALL -998` — move cursor up
- `CALL 64578` or `CALL -958` — clear text from cursor to bottom of window
- `CALL 64614` or `CALL -922` — move cursor down
- `CALL 64668` or `CALL -868` — clear text from cursor to end of line
- `CALL 64780` or `CALL -756` — wait for keypress
- `CALL 65152` or `CALL -384` — set inverse text mode
- `CALL 65156` or `CALL -380` — set normal text mode

```
PR# *aexpr*
```
Direct output to slot

- `PR#0` — set 40 column mode
- `PR#3` — set 80 column mode
- `PR#4` — write to Thunderclock

```
IN# *aexpr*
```
Direct output to slot

- `IN#0` — read input from keyboard or DOS
- `IN#4` — read from Thunderclock

### Functions

#### Numeric Functions

```
ABS( *aexpr* )
```
Absolute value of number

```
ATN( *aexpr* )
```
Arctangent of number

```
COS( *aexpr* )
```
Cosine of number

```
EXP( *aexpr* )
```
Raise e to number

```
INT( *aexpr* )
```
Integer part of number

```
LOG( *aexpr* )
```
Natural log of number

```
RND( *aexpr* )
```
Pseudo-random number generator.
 If *aexpr* is positive, returns a random number from 0 to 0.999....
 If *aexpr* is zero, repeats the last result.
 If *aexpr* is negative, reseeds the generator.

```
SGN( *aexpr* )
```
Sign of number (-1, 0, 1)

```
SIN( *aexpr* )
```
Sine of number

```
SQR( *aexpr* )
```
Square root of number

```
TAN( *aexpr* )
```
Tangent of number

#### String Functions

```
LEN( *sexpr* )
```
Length of string

```
LEFT$( *sexpr*, *aexpr* )
```
Left portion of (string, length)

```
MID$( *sexpr*, *aexpr* [, *aexpr*] )
```
Substring of (string, start character, length)

```
RIGHT$( *sexpr*, *aexpr* )
```
Right portion of (string, length)

#### Type Conversion Functions

```
ASC( *sexpr* )
```
ASCII code for first character of string

```
CHR$( *aexpr* )
```
Character at specified ASCII code point

```
STR$( *aexpr* )
```
String representation of number

```
VAL( *sexpr* )
```
Parse string into number

#### System Interaction Functions

```
FRE( *aexpr* )
```
Garbage collect strings (returns 0)

```
PDL( *aexpr* )
```
Paddle position (paddle number)

```
POS( *aexpr* )
```
Horizontal cursor position

```
SCRN( *aexpr*, *aexpr* )
```
Lores color at pixel (x,y)

```
USR( *aexpr* )
```
Execute assembly code at address, return accumulator value

#### User Defined Functions

```
FN *name*( *expr* )
```
Execute user defined function

#### Function Compatibility Shims

```
PEEK( *aexpr* )
```
Value at memory location

- `PEEK(32)` — Text window left edge
- `PEEK(33)` — Text window width
- `PEEK(34)` — Text window top edge
- `PEEK(35)` — Text window bottom
- `PEEK(36)` — Text cursor x
- `PEEK(37)` — Text cursor y
- `PEEK(78)` & `PEEK(79)` — Random-Number Field
- `PEEK(222)` — Last error code
- `PEEK(230)` — Hi-Res plotting page (32 = page 1, 64 = page 2)
- `PEEK(49152)` or `PEEK(-16384)` — Read Keyboard
- `PEEK(49168)` or `PEEK(-16368)` — Clear Keyboard strobe
- `PEEK(49178)` or `PEEK(-16358)` — See if text mode (> 127) or graphics mode (< 128)
- `PEEK(49179)` or `PEEK(-16357)` — See if mixed mode (> 127) or full mode (< 128)
- `PEEK(49180)` or `PEEK(-16356)` — See if page2 (> 127) or page1 (< 128)
- `PEEK(49181)` or `PEEK(-16355)` — See if hires mode (> 127) or lores mode (< 128)
- `PEEK(49182)` or `PEEK(-16354)` — See if mousetext mode (> 127)
- `PEEK(49183)` or `PEEK(-16353)` — See if 80-column mode (> 127)
- `PEEK(49200)` or `PEEK(-16336)` — Click Speaker (no-op)
- `PEEK(49248)` or `PEEK(-16288)` — Read Paddle Button #3
- `PEEK(49249)` or `PEEK(-16287)` — Read Paddle Button #0
- `PEEK(49250)` or `PEEK(-16286)` — Read Paddle Button #1
- `PEEK(49251)` or `PEEK(-16285)` — Read Paddle Button #2

### Operators

#### Comparison Operators

```
=
```
Equality

```
<
```
Less than

```
>
```
Greater than

```
<=
=<
```
Less than or equal

```
>=
=>
```
Greater than or equal

```
<>
><
```
Not equal

#### Boolean Operators

```
AND
```
Conjunction

```
OR
```
Disjunction

```
NOT
```
Negation

#### Arithmetic Operators

```
^
```
Exponentiation

```
*
```
Multiplication

```
/
```
Division

```
+
```
Addition

```
-
```
Subtraction

#### String Operators

```
+
```
String Concatenation

#### Operator Precedence

Operators are listed vertically in order of precedence, from highest to lowest. Operators on the same line are of the same priority, and in an expression are executed from left to right. This order differs from the order in some other dialects of BASIC, but does match Applesoft.



- `( )`
- `+ - NOT` (unary operators)
- `^`
- `* /`
- `+ -`
- `= < > <= =< >= => <> ><`
- `AND`
- `OR`


### Error Codes

Error codes can be determined by calling `PEEK(222)` in an ONERR handler.

```
0
```
Next without for

```
16
```
Syntax error

```
22
```
Return without gosub

```
42
```
Out of data

```
53
```
Illegal quantity

```
69
```
Overflow

```
77
```
Out of memory

```
90
```
Undefined statement

```
107
```
Bad subscript

```
120
```
Redimensioned array

```
133
```
Division by zero

163
Type mismatch

176
String too long — *Not generated*

191
Formula too complex

```
224
```
Undefined function

```
254
```
Re-enter

```
255
```
Break

### DOS 3.3 / ProDOS Quick Reference

See also

- [Apple II DOS & Commands FAQ](http://www.xs4all.nl/~fjkraan/comp/apple2faq/app2doscmdfaq.html)
- [Apple II Textfiles: the DOS 3.3 Anatomy](http://www.textfiles.com/apple/ANATOMY/)
- [Vectronic's Apple World DOS 3.3 and ProDOS Guide](http://vectronicsappleworld.com/appleii/dos.html)


#### DOS Commands

```
MON[,C][,I][,O]
```
Traces DOS 3.3 commands ('Commands', 'Input' and 'Output')

```
NOMON[,C][,I][,O]
```
Cancels tracing of DOS 3.3 commands ('Commands', 'Input' and 'Output')

```
OPEN *filename*[,L*len*]
```
Opens a text file.

```
APPEND *filename*
```
Appends to a text file.

```
CLOSE [*filename*]
```
Closes specified (or all) open text files.

```
POSITION *filename*[,R*num*]
```
Advances position in text file.

```
READ *filename*[,R*num*][,B*byte*]
```
Reads from a text file.

```
WRITE *filename*[,R*num*][,B*byte*]
```
Writes to a text file

```
DELETE *filename*
```
Delete a file

```
RENAME *oldname*,*newname*
```
Rename a file

```
PR# *slot*
```
Same as the BASIC command


#### DOS Error Codes

Error codes can be determined by calling `PEEK(222)` in an ONERR handler.

```
1
```
Language not available — *Not generated*

```
2
```
Range error — *Not generated*

```
4
```
Write protected — *Not generated*

```
5
```
End of data

```
6
```
File not found

```
7
```
Volume mismatch — *Not generated*

```
8
```
I/O error — *Not generated*

```
9
```
Disk full — *Not generated*

```
10
```
File locked — *Not generated*

```
11
```
Invalid option

```
12
```
No buffers available — *Not generated*

```
13
```
File type mismatch — *Not generated*

```
14
```
Program too large — *Not generated*

```
15
```
Not direct command — *Not generated*

### References

- [Apple II Programmer's Reference: Applesoft Commands](http://www.landsnail.com/a2ref.htm)
- [Applesoft BASIC Frequently Asked Questions (FAQ)](http://www.apple2.org/faq/FAQ.applesoft.html)
- [Beagle Bros. Peeks, Pokes & Pointers Chart (Colors, ASCII values, etc)](http://www.lazilong.com/apple_II/bbros/)
- [More Beagle Bros. Posters — including Apple Commands Chart, in PDF format](http://beagle.applearchives.com/posters.htm)
- [Applesoft Basic Programming Reference Manual](http://www.scribd.com/doc/232832/Applesoft-Basic-Programming-Reference-Manual)
