"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.class_dictionary = {}
        self.subroutine_dictionary = {}

        self.ind_dictionary = {"VAR": 0, "ARG": 0, "STATIC": 0, "FIELD": 0}

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.subroutine_dictionary = {}
        self.ind_dictionary["VAR"] = 0
        self.ind_dictionary["ARG"] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind in {"STATIC", "FIELD"} and name not in \
                self.class_dictionary.keys():
            self.class_dictionary[name] = [type, kind,
                                           self.ind_dictionary[kind]]
            self.ind_dictionary[kind] += 1

        elif name not in self.subroutine_dictionary.keys():
            self.subroutine_dictionary[name] = [type, kind,
                                                self.ind_dictionary[kind]]
            self.ind_dictionary[kind] += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        return self.ind_dictionary[kind]

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """

        if name in self.subroutine_dictionary.keys():
            return self.subroutine_dictionary[name][1]
        elif name in self.class_dictionary.keys():
            return self.class_dictionary[name][1]
        else:
            return "NONE"

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name in self.class_dictionary.keys():
            return self.class_dictionary[name][0]
        elif name in self.subroutine_dictionary.keys():
            return self.subroutine_dictionary[name][0]
        else:
            return "NONE"

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.class_dictionary.keys():
            return self.class_dictionary[name][2]
        elif name in self.subroutine_dictionary.keys():
            return self.subroutine_dictionary[name][2]
        else:
            return -1
