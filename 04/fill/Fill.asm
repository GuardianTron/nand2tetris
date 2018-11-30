// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(LOOP)

//set default color to white
@color
M=0

//set to black screen if key pressed
//otherwise leave color white and draw
@KBD
D=M
@DRAW
D;JEQ
@color
M=-1

(DRAW)
//initialize rows
@SCREEN
D=A
@8192
D=D+A
@regs
M=D

    (FILL)
    //load color to use
    @color
    D=M
    
    //color appropriate row
    @regs   
    A=M 
    M=D 

    //continue filling until all 32 rows filled
    @regs
    M=M-1
    @SCREEN
    D=A
    @regs
    D=D-M
    @FILL
    D;JLE
    


//restart once filled

@LOOP
0;JMP






