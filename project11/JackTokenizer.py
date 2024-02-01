"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

KEYWORDS = {"class": "CLASS", "constructor": "CONSTRUCTOR", "function":
            "FUNCTION", "method": "METHOD", "field": "FIELD", "static":
            "STATIC", "var": "VAR", "int": "INT", "char": "CHAR", "boolean":
            "BOOLEAN", "void": "VOID", "true": "TRUE", "false": "FALSE",
            "null": "NULL", "this": "THIS", "let": "LET", "do": "DO",
            "if": "IF", "else": "ELSE", "while": "WHILE", "return": "RETURN"}


SYMBOLS = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/",
           "&", "|", "<", ">", "=", "~", "^", "#"]


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.input = input_stream
        self.input_lines = input_stream.read().splitlines()

        self.input_lines[0].strip()

        while len(self.input_lines) > 0 and (len(self.input_lines[0]) == 0 or
             self.input_lines[0][0:2] == "/*" or self.input_lines[0][0:2] ==
                                             "//"):
            if self.input_lines[0][0:2] == "/*":
                while self.input_lines[0].find('*/') == -1:
                    self.input_lines.remove(self.input_lines[0])
                self.input_lines.remove(self.input_lines[0])
            else:
                self.input_lines.remove(self.input_lines[0])

            location = self.input_lines[0].find('//')
            while location != -1:
                if self.input_lines[0][:location].count('"') % 2 == 0:
                    self.input_lines[0] = self.input_lines[0][0:location]
                    break
                location = self.input_lines[0][location + 1:].find('//')
            self.input_lines[0].strip()

        self.curr_line = self.input_lines[0]
        self.curr_line_num = 0
        self.curr_token = ""
        self.type = ""
        self.placeholder = 0



    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        if len(self.curr_line) <= self.placeholder:
            if len(self.input_lines) <= self.curr_line_num + 1:
                return False
            self.remove_comments()
            while self.curr_line_num + 1 < len(self.input_lines) and (len(
                    self.input_lines[self.curr_line_num + 1]) == 0 or
                    len(self.input_lines[self.curr_line_num + 1].strip())
                                                                      == 0):

                self.input_lines.remove(self.input_lines[self.curr_line_num
                                                         + 1])
                if len(self.input_lines) <= self.curr_line_num + 1:
                    return False
                self.remove_comments()

            if len(self.input_lines) <= self.curr_line_num + 1:
                return False
            self.curr_line_num += 1
            self.curr_line = self.input_lines[self.curr_line_num]
            self.placeholder = 0
        return True

    def remove_comments(self):
        """
        Removes comments from input lines
        """
        location = self.input_lines[self.curr_line_num + 1].find('//')
        while location != -1:
            if self.input_lines[self.curr_line_num + 1][
               :location].count('"') % 2 == 0:
                self.input_lines[self.curr_line_num + 1] = self.input_lines[
                                           self.curr_line_num + 1][0:location]
                break
            location = self.input_lines[self.curr_line_num + 1][location +
                                                                1:].find('//')
        self.input_lines[self.curr_line_num + 1] = self.input_lines[
            self.curr_line_num + 1].strip()

        i = self.curr_line_num + 1
        location1 = self.input_lines[i].find('/*')
        location2 = self.input_lines[i].find('*/')
        while location1 != -1:
            if self.input_lines[i][:location1].count('"') % 2 == 1:
                break
            if location2 != -1:
                self.input_lines[i] = self.input_lines[i].replace(
                    self.input_lines[i][location1:location2 + 2], '')
                if len(self.input_lines[i]) == 0:
                    self.input_lines.remove(self.input_lines[i])
            else:
                self.input_lines.remove(self.input_lines[i])

                location2 = self.input_lines[i].find('*/')

                while i < len(self.input_lines) and location2 == -1:
                    self.input_lines.remove(self.input_lines[i])
                    location2 = self.input_lines[i].find('*/')
                self.input_lines[i] = self.input_lines[i][location2 + 2:]

            location1 = self.input_lines[i].find('/*')
            location2 = self.input_lines[i].find('*/')

        self.input_lines[self.curr_line_num + 1] = self.input_lines[
            self.curr_line_num + 1].strip()

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """

        while self.curr_line[self.placeholder] == ' ' or self.curr_line[
            self.placeholder] == '\t':
            self.placeholder += 1

        if self.curr_line[self.placeholder] in SYMBOLS:
            self.curr_token = self.curr_line[self.placeholder]
            self.placeholder += 1
            self.type = "SYMBOL"
            return

        i = self.placeholder
        if self.curr_line[i] == '"':
            i += 1
            while i < len(self.curr_line) and self.curr_line[i] != '"':
                i += 1
            self.curr_token = self.curr_line[self.placeholder + 1:i]
            self.placeholder = i + 1
            self.type = "STRING_CONST"
            return

        if self.curr_line[i].isnumeric():
            while i < len(self.curr_line) and self.curr_line[i].isnumeric():
                i += 1
            self.curr_token = self.curr_line[self.placeholder:i]
            self.placeholder = i
            self.type = "INT_CONST"
            return

        while i < len(self.curr_line) and self.curr_line[i] not in SYMBOLS \
                and self.curr_line[i] != " " and self.curr_line[i] != "\t":
            i += 1
        self.curr_token = self.curr_line[self.placeholder:i]
        self.placeholder = i
        if self.curr_token in KEYWORDS.keys():
            self.type = "KEYWORD"
            return
        if "\n" in self.curr_token:
            self.curr_token.replace("\n", "")

        self.type = "IDENTIFIER"

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can bes
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        return self.type

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return KEYWORDS[self.curr_token]

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        return self.curr_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        return self.curr_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        return int(self.curr_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        return self.curr_token
