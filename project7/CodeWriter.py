"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_file = output_stream
        self.file_name = ""
        self.i = 1

        self.ptrs = {"local": "LCL", "argument": "ARG", "this": "THIS",
                     "that": "THAT"}

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        self.file_name = filename

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given 
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        arithmetic = {"add": "@SP\nA=M\nA=A-1\nD=M\nA=A-1\nD=D+M\nM=D\n@SP"
                             "\nM=M-1\n",

                           "sub":
                               "@SP\nA=M\nA=A-1\nD=M\nA=A-1\nD=M-D\nM=D\n@SP\nM=M-1\n",

                           "neg": "@SP\nA=M\nA=A-1\nM=-M\n",

                           "eq":
                           "@SP\nM=M-1\n@SP\nA=M\nD=M\nA=A-1\nD=D-M\n"
                           "@EQ" + str(self.i) +
                           "\nD;JEQ\n@SP\nA=M-1\nM=0\n@EQ" + str(self.i) +
                           "\nD=A\n@3\nD=D+A\nA=D\n0;JMP\n("
                           "EQ" + str(self.i) + ")\n@SP\nA=M-1\nM=-1\n",

                           "gt":
                           "@SP\nM=M-1\nA=M\nD=M\n@SMALLER." + str(self.i) +
                            "\nD;JLT\n@SP\nA=M-1\nD=M\n@EQUAL." +
                           str(self.i) + "\nD;JGE\n@SP\nA=M-1\nM=0\n@END.GT." +
                           str(self.i) + "\n0;JMP\n(SMALLER." + str(self.i) +
                           ")\n@SP\nA=M-1\nD=M\n@EQUAL." + str(self.i) +
                           "\nD;JLT\n@SP\nA=M-1\nM=-1\n@END.GT." + str(self.i)
                           + "\n0;JMP\n(EQUAL." + str(self.i) +
                            ")\n@SP\nA=M\nD=M\nA=A-1\nD=D-M\n"
                           "@GT" + str(self.i) +
                           "\nD;JLT\n@SP\nA=M-1\nM=0\n@END.GT." + str(
                            self.i) + "\n0;JMP\n(GT" + str(self.i) +
                           ")\n@SP\nA=M-1\nM=-1\n(END.GT." + str(self.i) +
                               ")\n",

                           "lt":
                          "@SP\nM=M-1\nA=M\nD=M\n@SMALLER." + str(self.i) +
                          "\nD;JLT\n@SP\nA=M-1\nD=M\n@EQUAL." + str(
                          self.i) + "\nD;JGE\n@SP\nA=M-1\nM=-1\n@END.LT." +
                          str(self.i) + "\n0;JMP\n(SMALLER." + str(
                          self.i) + ")\n@SP\nA=M-1\nD=M\n@EQUAL." +
                          str(self.i) + "\nD;JLT\n@SP\nA=M-1\nM=0\n@END.LT."
                          + str(self.i) + "\n0;JMP\n(EQUAL." + str(self.i) +
                          ")\n@SP\nA=M\nD=M\nA=A-1\nD=D-M\n@LT" +
                          str( self.i) + "\nD;JGT\n@SP\nA=M-1\nM=0\n@END.LT."
                          + str(self.i) + "\n0;JMP\n(LT" + str(self.i) +
                          ")\n@SP\nA=M-1\nM=-1\n(END.LT." + str(self.i) + ")\n",

                           "or":
                           "@SP\nA=M\nA=A-1\nD=M\nA=A-1\nD=D|M\n@SP\nM=M-1\n"
                           "@SP\nA=M-1\nM=D\n",

                           "and":
                           "@SP\nA=M\nA=A-1\nD=M\nA=A-1\nD=D&M\n@SP\nM=M-1\n"
                           "@SP\nA=M-1\nM=D\n",

                           "not": "@SP\nA=M\nA=A-1\nM=!M\n",

                           "shiftleft": "@SP\nA=M-1\nM=M<<\n",

                           "shiftright": "@SP\nA=M-1\nM=M>>\n"}
        self.output_file.write(arithmetic[command])
        self.i += 1



    def latt(self, command: str, ptr: str, index: int):
        """Writes the assembly code that is the translation of a local /
        argument / that / this command, where command is either C_PUSH or C_POP

        Args:
            command (str): "C_PUSH" or "C_POP".
            ptr (str): the ptr to the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        if command == "C_PUSH":
            to_write = "@" + ptr + "\nD=M\n@" + str(index) + \
                       "\nD=D+A\nA=D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        else:
            to_write = "@" + ptr + "\nD=M\n@" + str(index) + \
                       "\nD=D+A\n@temp\nM=D\n@SP\nM=M-1\n@SP\nA=M\nD=M\n" \
                       "@temp\nA=M\nM=D\n"
        self.output_file.write(to_write)

    def constant(self, index: int):
        """Writes the assembly code that is the translation of a constant push
        command

        Args:
            index (int): the index in the memory segment.
        """
        to_write = "@" + str(index) + "\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        self.output_file.write(to_write)

    def static(self, command: str, index: int):
        """Writes the assembly code that is the translation of a static
        command, where command is either C_PUSH or C_POP

        Args:
            command (str): "C_PUSH" or "C_POP".
            index (int): the index in the memory segment.
        """
        if command == "C_PUSH":
            to_write = "@" + self.file_name + "." + str(index) + \
                       "\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        else:
            to_write = "@SP\nM=M-1\n@SP\nA=M\nD=M\n@" + self.file_name + \
                       "." + str(index) + "\nM=D\n"
        self.output_file.write(to_write)

    def temp(self, command: str, index: int):
        """Writes the assembly code that is the translation of a temp
        command, where command is either C_PUSH or C_POP

        Args:
            command (str): "C_PUSH" or "C_POP".
            index (int): the index in the memory segment.
        """
        if command == "C_PUSH":
            to_write = "@" + str(index) + "\nD=A\n@5" \
                       "\nA=A+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        else:
            to_write = "@" + str(index) + "\nD=A\n@5\nD=A+D\n@temp" \
                       "\nM=D\n@SP\nM=M-1\n@SP\nA=M\nD=M\n@temp\nA=M\nM=D\n"
        self.output_file.write(to_write)

    def pointer(self, command: str, index: int):
        """Writes the assembly code that is the translation of a pointer
        command, where command is either C_PUSH or C_POP

        Args:
            command (str): "C_PUSH" or "C_POP".
            index (int): the index in the memory segment.
        """
        if command == "C_PUSH":
            to_write = "@" + str(index) + \
                       "\nD=A\n@THIS\nA=A+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        else:
            to_write = "@" + str(index) + \
                       "\nD=A\n@THIS\nD=A+D\n@temp\nM=D\n@SP\nM=M-1\n@SP\n" \
                       "A=M\nD=M\n@temp\nA=M\nM=D\n"
        self.output_file.write(to_write)

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        if segment == "pointer":
            self.pointer(command, index)
        elif segment == "temp":
            self.temp(command, index)
        elif segment == "static":
            self.static(command, index)
        elif segment == "constant":
            self.constant(index)
        else:
            self.latt(command, self.ptrs[segment], index)


    def close(self) -> None:
        """Closes the output file."""
        self.output_file.close()
