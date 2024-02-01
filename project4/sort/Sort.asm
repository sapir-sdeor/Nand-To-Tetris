// This file is part of nand2tetris, as taught in The Hebrew University,
// and was written by Aviv Yaish, and is published under the Creative 
// Common Attribution-NonCommercial-ShareAlike 3.0 Unported License 
// https://creativecommons.org/licenses/by-nc-sa/3.0/

// An implementation of a sorting algorithm. 
// An array is given in R14 and R15, where R14 contains the start address of the 
// array, and R15 contains the length of the array. 
// You are not allowed to change R14, R15.
// The program should sort the array in-place and in descending order - 
// the largest number at the head of the array.
// You can assume that each array value x is between -16384 < x < 16384.
// You can assume that the address in R14 is at least >= 2048, and that 
// R14 + R15 <= 16383. 
// No other assumptions can be made about the length of the array.
// You can implement any sorting algorithm as long as its runtime complexity is 
// at most C*O(N^2), like bubble-sort. 

// Put your code here.

@i
M=-1
(LOOP)
	@i
	M=M+1
	D=M
	@R15
	D=D-M
	@END
	D;JGE
	@R14
	D=M
	@k
	M=D
	(LOOP2)
		@R15
		D=M
		@R14
		D=D+M
		@i
		D=D-M
		@k
		D=D-M
		D=D-1
		@LOOP
		D;JLE
		@k
		D=M
		A=D
		D=M
		@k
		A=M+1
		D=D-M
		@SWITCH
		D;JLT
		@k
		M=M+1
		@LOOP2
		0;JMP
		(SWITCH)
			@k
			A=M
			D=M
			@temp
			M=D
			@k
			A=M+1
			D=M
			@k
			A=M
			M=D
			@temp
			D=M
			@k
			A=M+1
			M=D
			@k
			M=M+1
			@LOOP2
			0;JMP
(END)
	@END
	0;JMP