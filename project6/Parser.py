"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads and assembly language 
    command, parses it, and provides convenient access to the commands 
    components (fields and symbols). In addition, removes all white space and 
    comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.input_lines = input_file.read().splitlines()
        while len(self.input_lines[0]) == 0 or self.input_lines[0][0:2] == '//':
            self.input_lines.remove(self.input_lines[0])
        location = self.input_lines[0].find('//')
        if location != -1:
            self.input_lines[0] = self.input_lines[0][0:location]
        self.input_lines[0] = self.input_lines[0].replace(' ', '')
        self.input_lines[0] = self.input_lines[0].replace("\t", "")
        self.curr_line = self.input_lines[0]
        self.curr_line_num = 0

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        while len(self.input_lines) > self.curr_line_num + 1 and (len(
                self.input_lines[self.curr_line_num + 1]) == 0 or
                self.input_lines[self.curr_line_num + 1][0:2] == '//'):
            self.input_lines.remove(self.input_lines[self.curr_line_num + 1])
        if len(self.input_lines) > self.curr_line_num + 1:
            return True
        else:
            return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        if self.has_more_commands():
            self.curr_line_num += 1
            location = self.input_lines[self.curr_line_num].find('//')
            if location != -1:
                self.input_lines[self.curr_line_num] = self.input_lines[self.curr_line_num][0:location]
            self.input_lines[self.curr_line_num] = self.input_lines[self.curr_line_num].replace(" ", "")
            self.input_lines[self.curr_line_num] = self.input_lines[
                self.curr_line_num].replace("\t", "")
            self.curr_line = self.input_lines[self.curr_line_num]


    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if len(self.curr_line) == 0:
            return ""
        if self.curr_line[0] == '(':
            return "L_COMMAND"
        elif self.curr_line[0] == '@':
            return "A_COMMAND"
        else:
            return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        if self.command_type() == "L_COMMAND":
            return self.curr_line[1:len(self.curr_line) - 1]
        else:
            return self.curr_line[1:len(self.curr_line)]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        dest_com = self.curr_line.split("=")
        if len(dest_com) < 2:
            return ""
        return dest_com[0]

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        s1 = self.curr_line.split("=")
        if len(s1) == 2:
            s2 = s1[1]
        else:
            s2 = s1[0]
        return s2.split(";")[0]

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        jump_com = self.curr_line.split(";")
        if len(jump_com) < 2:
            return ""
        return jump_com[1]
