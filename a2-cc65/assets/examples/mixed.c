#include <conio.h>

/* cc65 fastcall: unsigned char argument/result in A. X is zeroed on return. */
unsigned char __fastcall__ twice(unsigned char value);

int main(void)
{
    clrscr();
    cprintf("MIXED RESULT: %u\r\n", (unsigned)twice(21));
    cgetc();
    return 0;
}
