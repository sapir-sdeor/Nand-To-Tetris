"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer


class CompilationEngine:
    """Gets input file and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: typing.TextIO, output_stream:
    typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.output = output_stream
        self.tokenizer = JackTokenizer(input_stream)
        self.is_class_var = True
        self.is_subroutine = True
        self.tabs = ''

    def advance_tokenizer(self) -> bool:
        """
        Advances the tokenizer if there are more tokens
        :return: True if succeeded, False otherwise
        """
        if not self.tokenizer.has_more_tokens():
            return False
        self.tokenizer.advance()
        return True

    def write_identifier(self) -> None:
        """
        Writes the identifier to the output file
        """
        self.output.write(self.tabs + "<identifier> " +
                          self.tokenizer.identifier() + " </identifier>\n")

    def write_symbol(self) -> None:
        """
        Writes a symbol to the output file
        """
        if self.tokenizer.curr_token == '<':
            self.output.write(self.tabs + "<symbol> &lt; </symbol>\n")
        elif self.tokenizer.curr_token == '>':
            self.output.write(self.tabs + "<symbol> &gt; </symbol>\n")
        elif self.tokenizer.curr_token == '"':
            self.output.write(self.tabs + "<symbol> &quot; </symbol>\n")
        elif self.tokenizer.curr_token == '&':
            self.output.write(self.tabs + "<symbol> &amp; </symbol>\n")
        else:
            self.output.write(self.tabs + "<symbol> " + self.tokenizer.symbol()
                          + " </symbol>\n")

    def write_keyword(self) -> None:
        """
        Writes a keyword to the output file
        """
        self.output.write(self.tabs + "<keyword> " + self.tokenizer.keyword()
                          .lower() + " </keyword>\n")

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.output.write("<class>\n")
        self.tabs += '\t'

        self.advance_tokenizer()
        self.write_keyword()

        if not self.advance_tokenizer():
            return
        self.write_identifier()

        if not self.advance_tokenizer():
            return
        self.write_symbol()


        self.is_class_var = True
        while self.is_class_var:
            if not self.advance_tokenizer():
                return
            self.compile_class_var_dec()

        self.is_subroutine = True
        while self.is_subroutine:
            self.compile_subroutine()

        self.write_symbol()

        self.tabs = self.tabs[:-1]
        self.output.write("</class>\n")

    def write_type(self) -> None:
        """ Writes a type to the output file (keywords int / char / boolean
        or an identifier"""
        if self.tokenizer.token_type() != "KEYWORD":
            self.write_identifier()
        else:
            self.write_keyword()

    def write_varNames(self) -> None:
        """ Writes var names list to the output file """
        while self.tokenizer.token_type() == "SYMBOL":
            if self.tokenizer.symbol() != ';':
                self.write_symbol()
                if not self.advance_tokenizer():
                    return
                self.write_identifier()
            else:
                self.write_symbol()
                return
            if not self.advance_tokenizer():
                return

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        if self.tokenizer.keyword() not in ["FIELD", "STATIC"]:
            self.is_class_var = False
            return

        self.output.write(self.tabs + "<classVarDec>\n")
        self.tabs += '\t'

        self.write_keyword()

        if not self.advance_tokenizer():
            return
        self.write_type()

        if not self.advance_tokenizer():
            return
        self.write_identifier()

        if not self.advance_tokenizer():
            return
        self.write_varNames()

        self.tabs = self.tabs[:-1]
        self.output.write(self.tabs + "</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        if self.tokenizer.token_type() != "KEYWORD":
            self.is_subroutine = False
            return

        self.output.write(self.tabs + "<subroutineDec>\n")
        self.tabs += '\t'

        self.write_keyword()

        if not self.advance_tokenizer():
            return
        if self.tokenizer.token_type() == "KEYWORD" and \
                self.tokenizer.keyword() == "VOID":
            self.write_keyword()
        else:
            self.write_type()

        if not self.advance_tokenizer():
            return
        self.write_identifier()

        if not self.advance_tokenizer():
            return
        self.write_symbol()

        if not self.advance_tokenizer():
            return
        self.compile_parameter_list()
        self.write_symbol()

        # subroutine body
        self.output.write(self.tabs + "<subroutineBody>\n")
        self.tabs += '\t'

        if not self.advance_tokenizer():
            return
        self.write_symbol()

        if not self.advance_tokenizer():
            return
        while self.tokenizer.token_type() == "KEYWORD" and \
                self.tokenizer.keyword() == \
                "VAR":
            self.compile_var_dec()

        self.compile_statements()

        self.write_symbol()

        if not self.advance_tokenizer():
            return

        self.tabs = self.tabs[:-1]
        self.output.write(self.tabs + "</subroutineBody>\n")

        self.tabs = self.tabs[:-1]
        self.output.write(self.tabs + "</subroutineDec>\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.output.write(self.tabs + "<parameterList>\n")
        self.tabs += '\t'

        if self.tokenizer.symbol() == ")":
            self.tabs = self.tabs[:-1]
            self.output.write(self.tabs + "</parameterList>\n")
            return

        self.write_type()
        if not self.advance_tokenizer():
            return
        self.write_identifier()

        if not self.advance_tokenizer():
            return

        while self.tokenizer.symbol() != ")":
            self.write_symbol()
            if not self.advance_tokenizer():
                return
            self.write_type()
            if not self.advance_tokenizer():
                return
            self.write_identifier()

            if not self.advance_tokenizer():
                return

        self.tabs = self.tabs[:-1]
        self.output.write(self.tabs + "</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.output.write(self.tabs + "<varDec>\n")
        self.tabs += '\t'

        self.write_keyword()

        if not self.advance_tokenizer():
            return
        self.write_type()

        if not self.advance_tokenizer():
            return
        self.write_identifier()

        if not self.advance_tokenizer():
            return
        self.write_varNames()

        if not self.advance_tokenizer():
            return

        self.tabs = self.tabs[:-1]
        self.output.write(self.tabs + "</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.output.write(self.tabs + "<statements>\n")
        self.tabs += '\t'

        while self.tokenizer.token_type() == "KEYWORD":
            if self.tokenizer.keyword() == "DO":
                self.compile_do()
            elif self.tokenizer.keyword() == "LET":
                self.compile_let()
            elif self.tokenizer.keyword() == "WHILE":
                self.compile_while()
            elif self.tokenizer.keyword() == "RETURN":
                self.compile_return()
            elif self.tokenizer.keyword() == "IF":
                self.compile_if()

        self.tabs = self.tabs[:-1]
        self.output.write(self.tabs + "</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.output.write(self.tabs + "<doStatement>\n")
        self.tabs += '\t'

        self.write_keyword()

        if not self.advance_tokenizer():
            return
        self.write_identifier()
        if not self.advance_tokenizer():
            return
        self.write_subroutine_call()

        self.write_symbol()

        if not self.advance_tokenizer():
            return

        self.tabs = self.tabs[:-1]
        self.output.write(self.tabs + "</doStatement>\n")

    def write_subroutine_call(self) -> None:
        """ compiles a subroutine call"""

        if self.tokenizer.symbol() == '.':
            self.write_symbol()
            if not self.advance_tokenizer():
                return
            self.write_identifier()
            if not self.advance_tokenizer():
                return

        self.write_symbol()

        if not self.advance_tokenizer():
            return
        self.compile_expression_list()

        self.write_symbol()

        if not self.advance_tokenizer():
            return

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.output.write(self.tabs + "<letStatement>\n")
        self.tabs += '\t'

        self.write_keyword()

        if not self.advance_tokenizer():
            return
        self.write_identifier()

        if not self.advance_tokenizer():
            return
        if self.tokenizer.symbol() == '[':
            self.write_symbol()

            if not self.advance_tokenizer():
                return
            self.compile_expression()

            self.write_symbol()

            if not self.advance_tokenizer():
                return

        self.write_symbol()

        if not self.advance_tokenizer():
            return
        self.compile_expression()

        self.write_symbol()

        if not self.advance_tokenizer():
            return

        self.tabs = self.tabs[:-1]
        self.output.write(self.tabs + "</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.output.write(self.tabs + "<whileStatement>\n")
        self.tabs += '\t'

        self.write_keyword()

        if not self.advance_tokenizer():
            return
        self.write_symbol()

        if not self.advance_tokenizer():
            return
        self.compile_expression()

        self.write_symbol()

        if not self.advance_tokenizer():
            return
        self.write_symbol()

        if not self.advance_tokenizer():
            return
        self.compile_statements()

        self.write_symbol()

        if not self.advance_tokenizer():
            return

        self.tabs = self.tabs[:-1]
        self.output.write(self.tabs + "</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output.write(self.tabs + "<returnStatement>\n")
        self.tabs += '\t'

        self.write_keyword()

        if not self.advance_tokenizer():
            return

        if self.tokenizer.token_type() == "SYMBOL" and \
                self.tokenizer.curr_token == ';':
            self.write_symbol()
        else:
            self.compile_expression()
            self.write_symbol()

        if not self.advance_tokenizer():
            return

        self.tabs = self.tabs[:-1]
        self.output.write(self.tabs + "</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.output.write(self.tabs + "<ifStatement>\n")
        self.tabs += '\t'

        self.write_keyword()

        if not self.advance_tokenizer():
            return
        self.write_symbol()

        if not self.advance_tokenizer():
            return
        self.compile_expression()

        self.write_symbol()

        if not self.advance_tokenizer():
            return
        self.write_symbol()

        if not self.advance_tokenizer():
            return
        self.compile_statements()

        self.write_symbol()

        if not self.advance_tokenizer():
            return
        if self.tokenizer.token_type() == "KEYWORD" and \
                self.tokenizer.keyword() == "ELSE":
            self.write_keyword()

            if not self.advance_tokenizer():
                return
            self.write_symbol()

            if not self.advance_tokenizer():
                return
            self.compile_statements()

            self.write_symbol()

            if not self.advance_tokenizer():
                return

        self.tabs = self.tabs[:-1]
        self.output.write(self.tabs + "</ifStatement>\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.output.write(self.tabs + "<expression>\n")
        self.tabs += '\t'

        self.compile_term()

        while self.tokenizer.token_type() == "SYMBOL" and \
                self.tokenizer.symbol() in ['+', '-', '*', '/', '&', '|',
                                            '<', '>', '=']:
            self.write_symbol()

            if not self.advance_tokenizer():
                return
            self.compile_term()

        self.tabs = self.tabs[:-1]
        self.output.write(self.tabs + "</expression>\n")

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "."
        suffices to distinguish between the three possibilities. Any other
        token is not part of this term and should not be advanced over.
        """
        self.output.write(self.tabs + "<term>\n")
        self.tabs += '\t'

        if self.tokenizer.token_type() == "INT_CONST":
            self.output.write(self.tabs + "<integerConstant> " +
                          self.tokenizer.curr_token + " </integerConstant>\n")
            if not self.advance_tokenizer():
                return
        elif self.tokenizer.token_type() == "STRING_CONST":
            self.output.write(self.tabs + "<stringConstant> " +
                          self.tokenizer.curr_token + " </stringConstant>\n")
            if not self.advance_tokenizer():
                return
        elif self.tokenizer.token_type() == "KEYWORD" and \
                self.tokenizer.keyword() in ["TRUE", "FALSE", "NULL", "THIS"]:
            self.write_keyword()
            if not self.advance_tokenizer():
                return
        elif self.tokenizer.token_type() == "SYMBOL":
            if self.tokenizer.curr_token == '(':
                self.write_symbol()

                if not self.advance_tokenizer():
                    return
                self.compile_expression()

                self.write_symbol()
                if not self.advance_tokenizer():
                    return
            elif self.tokenizer.curr_token in {'-', '~', '^', '#'}:
                self.write_symbol()

                if not self.advance_tokenizer():
                    return
                self.compile_term()

        else:
            self.write_identifier()

            if not self.advance_tokenizer():
                return
            if self.tokenizer.symbol() == '[':
                self.write_symbol()

                if not self.advance_tokenizer():
                    return
                self.compile_expression()

                self.write_symbol()

                if not self.advance_tokenizer():
                    return
            elif self.tokenizer.symbol() in {'.', '('}:
                self.write_subroutine_call()

        self.tabs = self.tabs[:-1]
        self.output.write(self.tabs + "</term>\n")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""

        self.output.write(self.tabs + "<expressionList>\n")
        self.tabs += '\t'

        if self.tokenizer.token_type() == "SYMBOL" and \
                self.tokenizer.symbol() == ')':
            self.tabs = self.tabs[:-1]
            self.output.write(self.tabs + "</expressionList>\n")
            return

        self.compile_expression()

        while (self.tokenizer.token_type() == "SYMBOL" and
               self.tokenizer.symbol() == ","):
            self.write_symbol()

            if not self.advance_tokenizer():
                return
            self.compile_expression()

        self.tabs = self.tabs[:-1]
        self.output.write(self.tabs + "</expressionList>\n")
