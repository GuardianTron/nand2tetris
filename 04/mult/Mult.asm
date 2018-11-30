// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.
// Add multiplicand to itself 
// via loop number of times specified
// by multiplier


//set up accumulator
@product
M=0

//read in multiplier and save to new
//memory location for processing
//end if multiplier is zero
@R1
D=M
@END
D;JEQ
@multiplier
M=D

//load multiplicand and 
//end program to save if zero
@R0
D=M
@END
D;JEQ
@multiplicand
M=D

//optimization
//loop adds multiplicand to 
//itself multiplier times.
//If multiplier is larger than multiplicand
//swap to reduce loop time
@multiplier
D=M
@multiplicand
D=D-M
@MULT
D;JLT
//perform swap
@multiplicand //save multiplicand
D=M
@temp 
M=D
@multiplier //set multiplicand to value of multiplier
D=M
@multiplicand 
M=D
@temp //set multiplier to old multiplicand value
D=M
@multiplier
M=D



//perform multiplication
(MULT)
    //end if done multiplying - multiplier is zero
    @multiplier
    D=M
    @END
    D;JEQ

    //perform multiplication
    //fetch multiplicand
    @multiplicand
    D=M

    //add multiplicand to product and save result to ram 
    @product
    M=D+M

    //decremend multiplier
    @multiplier
    M=M-1

    //loop
    @MULT
    0;JMP

    





//end program

(END)
    //save product to R2
    @product
    D=M
    @R2
    M=D 
    (INFINITE)
    //infinte loop to end
    @INFINITE
    0;JMP






