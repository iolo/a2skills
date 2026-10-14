# Apple DOS 3.3 Reference

## Agent Navigation

Use this file for BASIC-facing DOS 3.3 command reminders.

- For disk-image manipulation, use `a2kit.md` or `applecommander.md`.
- For ProDOS commands, use `prodos.md`.
- For AppleSoft syntax, use `applesoft.md`.
- Be explicit when a command mutates a disk image, deletes data, or depends on current drive/slot state.

## Binary File Commands

- `BRUN name` Executes the binary file 'name'.
- `BSAVE name ,A ,L` Saves the file 'name' starting at A, with length L.
- `BLOAD name` Loads the binary file 'name'.

## BASIC Program Commands

- `FP` Activates applesoft basic and clears any program currently in memory.
- `INT` Activates integer basic and clears any program currently in memory.
- `RUN name` Executes 'name' from disk.
- `LOAD name` Loads 'name' from disk.
- `SAVE name` Saves the current program as 'name' on disk.
- `INIT name` Initializes a disk, erasing all data from it and setting the startup program to 'name'.
- `MAXFILES n` Sets the maximum number of open files.
- `MON {,C} {,I} {,O}` Selects whether Commands, Output, or Input are echoed to the screen.
- `NOMON {,C} {,I} {,O}` Disables printing of DOS operations.

## Programming Commands

- `CHAIN name` Allows integer basic programs to run other integer basic program.
- `PR# n` Re-directs output to slot n.
- `IN# n` Re-directs input from slot n.

## Filing Commands

- `CATALOG` Displays contents of the current disk directory.
- `RENAME oldname, newname` Changes the name of a disk file.
- `DELETE name` Deletes the file 'name'.
- `LOCK name` Prevents the file 'name' from being deleted, renamed or changed.
- `UNLOCK name` Removes file locking.
- `VERIFY name` Checks to see than an entire file is readable.

## Text File Commands

- `OPEN name` Opens a text file for reading.
- `CLOSE name` Closes a text file.
- `READ name` Sets the file 'name' to read mode.
- `WRITE name` Sets the file 'name' to write mode.
- `APPEND name` Sets write mode for 'name' at the end of the current file.
- `POSITION name,x` Moves the record pointer for 'name' to the position specified by x.
- `EXEC name` Reads text from file 'name' entering it as though it were typed from the keyboard.
