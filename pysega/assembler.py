import os
import sys
import ply.lex as lex
import ply.yacc as yacc
import pprint
import logging
from pysega.cpu.m68k.lexer import Lexer
from pysega.cpu.m68k.parser import Parser

class Assembler(object):
    def __init__(self):
        data = """MOVE D1
                  MOVE D1, D2
                  MOVE A1, D1
                  SUB A1,D1
                  SUB.W A1,D1"""

        # Set up a logging object
        logging.basicConfig(
            level = logging.DEBUG,
            filename = "parselog.txt",
            filemode = "w",
            format = "%(filename)10s:%(lineno)4d:%(message)s"
        )
        log = logging.getLogger()

        targetLexer = Lexer()
        lexer = lex.lex(module=targetLexer, debug=True)
        targetParser = Parser(targetLexer.tokens)
        parser = yacc.yacc(module=targetParser, debug=True, debuglog=log)
        test = parser.parse(data)
        print(test)
        for instruction in test[1]:
            print(instruction)
            instruction[0](instruction[0],instruction[1:])
