import os
import sys
import ply.lex as lex
import ply.yacc as yacc
from pysega.cpu.m68k.lexer import Lexer as Target

class Assembler(object):
    def __init__(self):
        data = """  MOVE D1,D2
        MOVE D2,D3
        MOVE (#1919, D2)"""
        init = lex.lex(module=Target(), debug=True)
        # Give the lexer some input
        init.input(data)

        # Tokenize
        while True:
            tok = init.token()
            if not tok:
                break      # No more input
            print(tok)
