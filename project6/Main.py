"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """

    # *Initialization*
    # Initialize the symbol table with all the predefined symbols and their
    # pre-allocated RAM addresses, according to section 6.2.3 of the book.
    # *First Pass*
    # Go through the entire assembly program, line by line, and build the symbol
    # table without generating any code. As you march through the program lines,
    # keep a running number recording the ROM address into which the current
    # command will be eventually loaded.
    # This number starts at 0 and is incremented by 1 whenever a C-instruction
    # or an A-instruction is encountered, but does not change when a label
    # pseudo-command or a comment is encountered. Each time a pseudo-command
    # (Xxx) is encountered, add a new entry to the symbol table, associating
    # Xxx with the ROM address that will eventually store the next command in
    # the program.
    # This pass results in entering all the program labels along with their
    # ROM addresses into the symbol table.
    # The program variables are handled in the second pas

    table = SymbolTable()
    parser = Parser(input_file)
    line_num = 0
    parser.curr_line_num = -1
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == "L_COMMAND":
            table.add_entry(parser.symbol(), line_num)
        elif len(parser.curr_line) != 0:
            line_num += 1


    # *Second Pass*
    # Now go again through the entire program, and parse each line.
    # Each time a symbolic A-instruction is encountered, namely, @Xxx where Xxx
    # is a symbol and not a number, look up Xxx in the symbol table.
    # If the symbol is found in the table, replace it with its numeric meaning
    # and complete the command translation.
    # If the symbol is not found in the table, then it must represent a new
    # variable. To handle it, add the pair (Xxx,n) to the symbol table, where n
    # is the next available RAM address, and complete the command translation.
    # The allocated RAM addresses are consecutive numbers, starting at address
    # 16 (just after the addresses allocated to the predefined symbols).
    # After the command is translated, write the translation to the output file.
    code = Code()
    parser.curr_line_num = -1
    n = 16
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == "A_COMMAND":
            if not parser.symbol().isnumeric():
                if not table.contains(parser.symbol()):
                    table.add_entry(parser.symbol(), n)
                    n += 1
                binary = str(format(table.get_address(parser.symbol()), "b"))
                while len(binary) != 16:
                    binary = "0" + binary
                output_file.write(binary)
            else:
                binary = str(format(int(parser.symbol()), "b"))
                while len(binary) != 16:
                    binary = "0" + binary
                output_file.write(binary)
            output_file.write("\n")
        elif parser.command_type() == "C_COMMAND":
            dest_str = parser.dest()
            comp_str = parser.comp()
            jump_str = parser.jump()
            if "<<" in comp_str or ">>" in comp_str:
                output_file.write("101")
            else:
                output_file.write("111")
            output_file.write(code.comp(comp_str))
            output_file.write(code.dest(dest_str))
            output_file.write(code.jump(jump_str))
            output_file.write("\n")


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
