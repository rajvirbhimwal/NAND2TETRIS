// Box.asm for K = 36
// Draws a 16-pixel wide (1 word) by 20-row tall black box at row 36 (left edge)
// while any key is pressed, and clears it when released.

(LOOP)
    // Check keyboard memory map (RAM[24576])
    @KBD
    D=M
    @SET_WHITE
    D;JEQ           // If KBD == 0 (no key pressed), set color = 0 (white)

    @color
    M=-1            // Key pressed: set color = -1 (16 black pixels)
    @DRAW_INIT
    0;JMP

(SET_WHITE)
    @color
    M=0             // No key pressed: set color = 0 (16 white pixels)

(DRAW_INIT)
    // Calculate starting address: SCREEN (16384) + 36 * 32 (1152) = 17536
    @17536
    D=A
    @addr
    M=D             // addr = current screen word address

    @20
    D=A
    @rows
    M=D             // rows = 20 rows remaining

(DRAW_LOOP)
    @rows
    D=M
    @LOOP
    D;JEQ           // If rows == 0, box is complete; return to polling KBD

    // Write current color (-1 or 0) to RAM[addr]
    @color
    D=M
    @addr
    A=M
    M=D

    // Advance pointer down by 1 row (+32 words)
    @32
    D=A
    @addr
    M=M+D

    // Decrement row counter
    @rows
    M=M-1

    @DRAW_LOOP
    0;JMP