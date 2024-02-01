"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

from VMWriter import VMWriter
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable

segments = {"STATIC": "STATIC", "FIELD": "THIS", "ARG": "ARG", "VAR":
            "LOCAL"}

arithmetics = {'+': "add", '-': "sub", '&': "and", '|': "or", '<': "lt",
               '>': "gt", '=': "eq"}


class CompilationEngine:
    """Gets input file and emits its parsed structure into an
    output stream.
    """
    i = 1

    def __init__(self, input_stream: typing.TextIO, output_stream:
        typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.output = output_stream
        self.vm_writer = VMWriter(self.output)
        self.tokenizer = JackTokenizer(input_stream)
        self.symbol_table = SymbolTable()
        self.is_class_var = True
        self.is_subroutine = True

        self.class_name = ""
        self.n_args = 0

        self.kind = ""
        self.type = ""
        self.is_in_symboltable = False

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
        if self.is_in_symboltable:
            self.symbol_table.define(self.tokenizer.identifier(), self.type,
                                     self.kind)

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.advance_tokenizer()

        if not self.advance_tokenizer():
            return
        self.class_name = self.tokenizer.identifier()

        if not self.advance_tokenizer():
            return

        self.is_in_symboltable = True
        self.is_class_var = True
        while self.is_class_var:
            if not self.advance_tokenizer():
                return
            self.compile_class_var_dec()

        self.is_in_symboltable = False
        self.is_subroutine = True
        while self.is_subroutine:
            self.compile_subroutine()

    def write_type(self) -> None:
        """ Writes a type to the output file (keywords int / char / boolean
        or an identifier"""
        if self.tokenizer.token_type() != "KEYWORD":
            self.type = self.tokenizer.curr_token
        else:
            self.type = self.tokenizer.keyword()

    def write_varNames(self) -> None:
        """ Writes var names list to the output file """
        while self.tokenizer.token_type() == "SYMBOL":
            if self.tokenizer.symbol() != ';':
                if not self.advance_tokenizer():
                    return
                self.symbol_table.define(self.tokenizer.identifier(),
                                         self.type,
                                         self.kind)
            else:
                return
            if not self.advance_tokenizer():
                return

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        if self.tokenizer.keyword() not in ["FIELD", "STATIC"]:
            self.is_class_var = False
            return

        self.kind = self.tokenizer.keyword()

        if not self.advance_tokenizer():
            return

        self.write_type()

        if not self.advance_tokenizer():
            return
        self.symbol_table.define(self.tokenizer.identifier(),
                                 self.type,
                                 self.kind)

        if not self.advance_tokenizer():
            return
        self.write_varNames()

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        if self.tokenizer.token_type() != "KEYWORD":
            self.is_subroutine = False
            return

        self.symbol_table.start_subroutine()

        subroutine_type = self.tokenizer.keyword()
        if subroutine_type == "METHOD":
            self.symbol_table.define("this", self.class_name, "ARG")

        if not self.advance_tokenizer():
            return

        if not self.advance_tokenizer():
            return
        func_name = self.class_name + "." + self.tokenizer.identifier()

        if not self.advance_tokenizer():
            return
        if not self.advance_tokenizer():
            return
        self.compile_parameter_list()

        if not self.advance_tokenizer():
            return
        if not self.advance_tokenizer():
            return

        while self.tokenizer.token_type() == "KEYWORD" and \
                self.tokenizer.keyword() == "VAR":
            self.compile_var_dec()

        self.vm_writer.write_function(func_name,
                                      self.symbol_table.var_count("VAR"))

        if subroutine_type == "CONSTRUCTOR":
            self.vm_writer.write_push("CONST", self.symbol_table.var_count(
                "FIELD"))
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("POINTER", 0)
        if subroutine_type == "METHOD":
            self.vm_writer.write_push("ARG", 0)
            self.vm_writer.write_pop("POINTER", 0)

        self.compile_statements()

        if not self.advance_tokenizer():
            return


    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        if self.tokenizer.symbol() == ")":
            return

        self.is_in_symboltable = True
        self.kind = "ARG"

        self.write_type()

        if not self.advance_tokenizer():
            return
        self.symbol_table.define(self.tokenizer.identifier(), self.type,
                                 self.kind)

        if not self.advance_tokenizer():
            return

        while self.tokenizer.symbol() != ")":
            if not self.advance_tokenizer():
                return
            self.write_type()

            if not self.advance_tokenizer():
                return
            self.symbol_table.define(self.tokenizer.identifier(), self.type,
                                     self.kind)

            if not self.advance_tokenizer():
                return

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.is_in_symboltable = True

        self.kind = self.tokenizer.keyword()

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

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.is_in_symboltable = False

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

    def compile_do(self) -> None:
        """Compiles a do statement."""
        if not self.advance_tokenizer():
            return
        subroutine_name = self.tokenizer.identifier()
        if not self.advance_tokenizer():
            return

        self.write_subroutine_call(subroutine_name)

        self.vm_writer.write_pop("TEMP", 0)

        if not self.advance_tokenizer():
            return

    def write_subroutine_call(self, name: str) -> None:
        """ compiles a subroutine call"""

        if self.tokenizer.symbol() == '.':
            if not self.advance_tokenizer():
                return

            if name in self.symbol_table.class_dictionary.keys() or name in \
                    self.symbol_table.subroutine_dictionary.keys():
                self.vm_writer.write_push(segments[self.symbol_table.kind_of(
                    name)], self.symbol_table.index_of(name))

                name = self.symbol_table.type_of(name) + '.' + \
                       self.tokenizer.identifier()

                self.n_args = 1
            else:
                name = name + '.' + self.tokenizer.identifier()
                self.n_args = 0

            if not self.advance_tokenizer():
                return
        else:
            name = self.class_name + '.' + name
            self.vm_writer.write_push("POINTER", 0)
            self.n_args = 1

        if not self.advance_tokenizer():
            return

        self.compile_expression_list()

        self.vm_writer.write_call(name, self.n_args)

        if not self.advance_tokenizer():
            return

    def compile_let(self) -> None:
        """Compiles a let statement."""
        if not self.advance_tokenizer():
            return
        identifier = self.tokenizer.identifier()

        is_array = False

        if not self.advance_tokenizer():
            return
        if self.tokenizer.symbol() == '[':
            is_array = True
            self.vm_writer.write_push(segments[self.symbol_table.kind_of(
                identifier)], self.symbol_table.index_of(identifier))
            if not self.advance_tokenizer():
                return
            self.compile_expression()

            self.vm_writer.write_arithmetic("ADD")

            if not self.advance_tokenizer():
                return

        if not self.advance_tokenizer():
            return
        self.compile_expression()
        if is_array:
            self.vm_writer.write_pop("TEMP", 0)
            self.vm_writer.write_pop("POINTER", 1)
            self.vm_writer.write_push("TEMP", 0)
            self.vm_writer.write_pop("THAT", 0)
        else:
            self.vm_writer.write_pop(segments[self.symbol_table.kind_of(
                identifier)], self.symbol_table.index_of(identifier))

        if not self.advance_tokenizer():
            return

    def compile_while(self) -> None:
        """Compiles a while statement."""
        label1 = "WHILE" + str(CompilationEngine.i)
        CompilationEngine.i += 1
        label2 = "ENDWHILE" + str(CompilationEngine.i)
        CompilationEngine.i += 1

        self.vm_writer.write_label(label1)

        if not self.advance_tokenizer():
            return

        if not self.advance_tokenizer():
            return
        self.compile_expression()

        self.vm_writer.write_arithmetic("NOT")

        self.vm_writer.write_if(label2)

        if not self.advance_tokenizer():
            return

        if not self.advance_tokenizer():
            return
        self.compile_statements()

        self.vm_writer.write_goto(label1)

        self.vm_writer.write_label(label2)

        if not self.advance_tokenizer():
            return

    def compile_return(self) -> None:
        """Compiles a return statement."""
        if not self.advance_tokenizer():
            return

        if self.tokenizer.token_type() == "SYMBOL" and \
                self.tokenizer.curr_token == ';':
            self.vm_writer.write_push("CONST", 0)
        else:
            self.compile_expression()

        self.vm_writer.write_return()

        if not self.advance_tokenizer():
            return

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        label1 = "ELSE" + str(CompilationEngine.i)
        CompilationEngine.i += 1
        label2 = "ENDIF" + str(CompilationEngine.i)
        CompilationEngine.i += 1

        if not self.advance_tokenizer():
            return

        if not self.advance_tokenizer():
            return
        self.compile_expression()

        self.vm_writer.write_arithmetic("NOT")

        self.vm_writer.write_if(label1)

        if not self.advance_tokenizer():
            return

        if not self.advance_tokenizer():
            return
        self.compile_statements()

        self.vm_writer.write_goto(label2)

        self.vm_writer.write_label(label1)

        if not self.advance_tokenizer():
            return
        if self.tokenizer.token_type() == "KEYWORD" and \
                self.tokenizer.keyword() == "ELSE":
            if not self.advance_tokenizer():
                return
            if not self.advance_tokenizer():
                return
            self.compile_statements()
            if not self.advance_tokenizer():
                return

        self.vm_writer.write_label(label2)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()

        while self.tokenizer.token_type() == "SYMBOL" and \
                self.tokenizer.symbol() in ['+', '-', '*', '/', '&', '|',
                                            '<', '>', '=']:
            arithmetic_op = self.tokenizer.symbol()

            if not self.advance_tokenizer():
                return
            self.compile_term()

            if arithmetic_op == '*':
                self.vm_writer.write_call("Math.multiply", 2)
            elif arithmetic_op == '/':
                self.vm_writer.write_call("Math.divide", 2)
            else:
                self.vm_writer.write_arithmetic(arithmetics[arithmetic_op])

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

        if self.tokenizer.token_type() == "INT_CONST":
            self.vm_writer.write_push("CONST", self.tokenizer.int_val())
            if not self.advance_tokenizer():
                return

        elif self.tokenizer.token_type() == "STRING_CONST":
            string = self.tokenizer.string_val()
            self.vm_writer.write_push("CONST", len(string))
            self.vm_writer.write_call("String.new", 1)
            for i in range(len(string)):
                self.vm_writer.write_push("CONST", ord(string[i]))
                self.vm_writer.write_call("String.appendChar", 2)
            if not self.advance_tokenizer():
                return

        elif self.tokenizer.token_type() == "KEYWORD":
            if self.tokenizer.keyword() == "TRUE":
                self.vm_writer.write_push("CONST", 1)
                self.vm_writer.write_arithmetic("NEG")
            elif self.tokenizer.keyword() in {"FALSE", "NULL"}:
                self.vm_writer.write_push("CONST", 0)
            else:
                self.vm_writer.write_push("POINTER", 0)
            if not self.advance_tokenizer():
                return

        elif self.tokenizer.token_type() == "SYMBOL":
            if self.tokenizer.curr_token == '(':
                if not self.advance_tokenizer():
                    return
                self.compile_expression()
                if not self.advance_tokenizer():
                    return

            elif self.tokenizer.curr_token in {'-', '~', '^', '#'}:
                onary_op = self.tokenizer.symbol()
                if not self.advance_tokenizer():
                    return
                self.compile_term()
                if onary_op == '-':
                    self.vm_writer.write_arithmetic("NEG")
                elif onary_op == '~':
                    self.vm_writer.write_arithmetic("NOT")
                elif onary_op == '^':
                    self.vm_writer.write_arithmetic("shiftleft")
                else:
                    self.vm_writer.write_arithmetic("shiftright")

        else:
            identifier = self.tokenizer.identifier()

            if not self.advance_tokenizer():
                return
            if self.tokenizer.symbol() == '[':
                self.vm_writer.write_push(segments[self.symbol_table.kind_of(
                    identifier)], self.symbol_table.index_of(identifier))

                if not self.advance_tokenizer():
                    return
                self.compile_expression()

                self.vm_writer.write_arithmetic("ADD")
                self.vm_writer.write_pop("POINTER", 1)
                self.vm_writer.write_push("THAT", 0)
                if not self.advance_tokenizer():
                    return
            elif self.tokenizer.symbol() in {'.', '('}:
                self.write_subroutine_call(identifier)
            else:
                self.vm_writer.write_push(segments[self.symbol_table.kind_of(
                    identifier)], self.symbol_table.index_of(identifier))

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        if self.tokenizer.token_type() == "SYMBOL" and \
                self.tokenizer.symbol() == ')':
            return

        self.compile_expression()
        self.n_args += 1
        while (self.tokenizer.token_type() == "SYMBOL" and
               self.tokenizer.symbol() == ","):

            if not self.advance_tokenizer():
                return
            self.compile_expression()
            self.n_args += 1
