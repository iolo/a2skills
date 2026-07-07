# PRODOS Reference

## Agent Navigation

Use this file for BASIC-facing ProDOS command reminders.

- For disk-image manipulation, use `a2kit.md` or `applecommander.md`.
- For DOS 3.3 commands, use `appledos.md`.
- For AppleSoft syntax, use `applesoft.md`.
- Be explicit about current prefix, file type, and whether the workflow is ProDOS rather than DOS 3.3.

## Binary File Commands

- `BRUN name` Executes the binary file 'name' from disk.
- `BSAVE name,A,L` Saves the binary file 'name', starting at address A, length L to disk.
- `BLOAD name` Loads the binary file 'name' from disk.

## BASIC Program Commands

- `-` Executes a BASIC, binary or EXEC file.
- `RUN name` Executes the BASIC program 'name' from disk.
- `LOAD name` Loads the file 'name' from disk.
- `SAVE name` Saves the current program as 'name' on disk.

## Programming Commands

- `CHAIN name` Allows one program to run another.
- `STORE name` Stores all basic variables to disk.
- `RESTORE name` Restores all basic variables from disk.
- `PR# n` Re-directs character output to slot n.
- `IN# n` Re-directs character input from slot n.
- `FRE` Performs applesoft house cleaning.
- `BYE` Exits current program.

## Filing Commands

- `CAT` Displays contents of the current disk directory (40 col).
- `CATALOG` Displays contents of the current disk directory (80 col).
- `PREFIX pathname` Displays the current prefix, or sets the prefix.
- `CREATE name` Creates a new disk file.
- `RENAME oldname, newname` Changes the name of a disk file.
- `DELETE name` Removes a file from the disk.
- `LOCK name` Prevents the file 'name' from being deleted, renamed or changed.
- `UNLOCK name` Removes file locking.
- `VERIFY name` Checks to see than an entire file is readable.

## Text File Commands

- `OPEN name` Opens a text file on disk.
- `CLOSE name` Closes a text file on disk.
- `READ name` Sets read mode for 'name'.
- `WRITE name` Sets write mode for 'name'.
- `APPEND name` Sets write mode at the end of 'name'.
- `FLUSH name` Writes any unwritten information to name.
- `POSITION name` Moves the file pointer of 'name'.
- `EXEC name` Reads text from a file, passing it to the current program as though it were typed from the keyboard.
