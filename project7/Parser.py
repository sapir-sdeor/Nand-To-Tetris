"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        self.input_lines = input_file.read().splitlines()
        while len(self.input_lines[0]) == 0 or self.input_lines[0][0:2] == \
                "//":
            self.input_lines.remove(self.input_lines[0])
        location = self.input_lines[0].find('//')
        if location != -1:
            self.input_lines[0] = self.input_lines[0][0:location]
        self.input_lines[0].strip()
        self.input_lines[0] = self.input_lines[0].replace(
            "\t", "")
        self.curr_line = self.input_lines[0]
        self.curr_line_num = 0
        self.command_dic = {"push": "C_PUSH", "pop": "C_POP",
                            "label": "C_LABEL", "goto": "C_GOTO",
                            "if-goto": "C_IF", "function": "C_FUNCTION",
                            "return": "C_RETURN", "call": "C_CALL", "add":
                            "C_ARITHMETIC", "sub": "C_ARITHMETIC",
                            "neg": "C_ARITHMETIC", "eq": "C_ARITHMETIC",
                            "gt": "C_ARITHMETIC", "and": "C_ARITHMETIC",
                            "lt": "C_ARITHMETIC", "or": "C_ARITHMETIC",
                            "not": "C_ARITHMETIC", "shiftleft":
                            "C_ARITHMETIC", "shiftright": "C_ARITHMETIC"}


    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        while self.curr_line_num + 1 < len(self.input_lines) and (len(
                self.input_lines[self.curr_line_num + 1]) == 0 or
                self.input_lines[self.curr_line_num + 1][0:2] == "//"):
            self.input_lines.remove(self.input_lines[self.curr_line_num + 1])
        return self.curr_line_num + 1 < len(self.input_lines)

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        if not self.has_more_commands():
            return
        self.curr_line_num += 1
        location = self.input_lines[self.curr_line_num].find('//')
        if location != -1:
            self.input_lines[self.curr_line_num] = self.input_lines[self.curr_line_num][0:location]
        self.input_lines[self.curr_line_num] = self.input_lines[
            self.curr_line_num].replace("\t", "")
        self.input_lines[self.curr_line_num].strip()
        self.curr_line = self.input_lines[self.curr_line_num]


    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        command = self.curr_line.split(' ')
        return self.command_dic[command[0]]

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        command = self.curr_line.split(' ')
        if self.command_type() == "C_ARITHMETIC":
            return command[0]
        else:
            return command[1]


    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        command = self.curr_line.split(' ')
        return int(command[2])
