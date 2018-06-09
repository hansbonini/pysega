#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import io
import logging
import os
import sys
import textwrap

import ply.lex as lex
import ply.yacc as yacc


class Register(object):
    SPECIAL_REGISTERS = ['PC', 'SR', 'CCR']

    def __init__(self, register):
        if register not in self.SPECIAL_REGISTERS:
            self.type = 'Dn' if register[0] == 'D' else 'An'
            self.value = bin(int(register[1], 10))[2:]
        else:
            self.type = register
            self.value = register


class AddrMode_DnDirect(object):
    def __init__(self, params):
        self.type = 'DnDirect'
        self.param = params
        self.mask = 0x00001


class AddrMode_AnDirect(object):
    def __init__(self, params):
        self.type = 'AnDirect'
        self.params = params
        self.mask = 0x00002


class AddrMode_AnIndirect(object):
    def __init__(self, params):
        self.type = 'AnIndirect'
        self.params = params
        self.mask = 0x00004


class AddrMode_AnIndirectPost(object):
    def __init__(self, params):
        self.type = 'AnIndirectPost'
        self.params = params
        self.mask = 0x00008


class AddrMode_AnIndirectPre(object):
    def __init__(self, params):
        self.type = 'AnIndirectPre'
        self.params = params
        self.mask = 0x00010


class AddrMode_AnIndirectDisplacement(object):
    def __init__(self, params):
        self.type = 'AnIndirectDisplacement'
        self.params = params
        self.mask = 0x00020


class AddrMode_AnIndirectIndex(object):
    def __init__(self, params):
        self.type = 'AnIndirectIndex'
        self.params = params
        self.mask = 0x00040


class AddrMode_AbsShort(object):
    def __init__(self, params):
        self.type = 'AbsShort'
        self.params = params
        self.mask = 0x00080


class AddrMode_AbsLong(object):
    def __init__(self, params):
        self.type = 'AbsLong'
        self.params = params
        self.mask = 0x00100


class AddrMode_Imm(object):
    def __init__(self, params):
        self.type = 'Imm'
        self.params = params
        self.mask = 0x00800


class Instruction(object):
    def __init__(self, instruction, size='BYTE', params=[]):
        self.instruction = instruction
        self.size = size
        self.params = params


class AssemblerLexer(object):
    ''' Motorola 68000 Conditions Set '''
    ASM_CONDITIONS = [
        'CC', 'CS', 'EQ', 'GE', 'GT', 'HI',
        'LE', 'LS', 'LT', 'MI', 'NE', 'PL',
        'VC', 'VS'
    ]

    ''' Motorola 68000 Instructions Set '''
    ASM_INSTRUCTIONS = [
        'ABCD', 'ADD', 'ADDA', 'ADDI', 'ADDQ', 'ADDX',
        'AND', 'ANDI', 'ASL', 'ASR', 'Bcc', 'BCHG',
        'BCLR', 'BRA', 'BSET', 'BSR', 'BTST', 'CHK', 'CLR', 'CMP',
        'CMPA', 'CMPI', 'CMPM', 'DBcc', 'DBF', 'DBRA', 'DC', 'DIVS', 'DIVU',
        'EOR', 'EORI', 'EXG', 'EXT', 'ILLEGAL', 'JMP',
        'JSR', 'LEA', 'LINK', 'LSL', 'LSR', 'MOVE', 'MOVEA', 'MOVEM',
        'MOVEP', 'MOVEQ', 'MULS', 'MULU', 'NBCD', 'NEG', 'NEGX',
        'NOP', 'NOT', 'OR', 'ORI', 'PEA', 'RESET', 'ROL', 'ROR',
        'ROXL', 'ROXR', 'RTE', 'RTR', 'RTS', 'SBCD', 'Scc',
        'STOP', 'SUB', 'SUBA', 'SUBI', 'SUBQ', 'SUBX', 'SWAP',
        'TAS', 'TRAP', 'TRAPV', 'TST', 'UNLK',
    ]

    ''' Motorola 68000 Registers Set '''
    ASM_REGISTERS = [
        'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7',
        'A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7',
        'PC', 'SR', 'CCR'
    ]

    ''' Motorola 68000 Sizes Set '''
    ASM_SIZES = [
        'BYTE', 'WORD', 'LONG'
    ]

    tokens = (
        'ID',
        'INSTRUCTION', 'CONDITIONAL_INSTRUCTION', 'SIZE', 'REGISTER',
        'LABEL', 'COMMENT',
        'STRING', 'BINARY', 'DECIMAL', 'OCTAL', 'HEXADECIMAL',
        'REFERENCE',
        'INDENT',
        'DOT', 'COMMA', 'COLON', 'HASH', 'DOLLAR',
        'LPAR', 'RPAR',
        'PLUS', 'MINUS', 'DIV', 'MULT'
    )

    """ Lexer Methods """

    def __init__(self, **kwargs):
        self._indented = False
        self._errors = []
        self._line = []
        self._lines = []
        self.lexer = lex.lex(module=self, **kwargs)

    def get_errors(self):
        return self._errors

    """ Return Instructions List """

    def get_instructions_list(self):
        instruction_list = []
        conditional_instruction_list = []
        for instruction in self.ASM_INSTRUCTIONS:
            if "cc" not in instruction:
                instruction_list.append(instruction)
            else:
                for conditional_instruction in self.ASM_CONDITIONS:
                    conditional_instruction_list.append(
                        instruction.replace('cc', conditional_instruction))
        return instruction_list, conditional_instruction_list

    """ Lexer Roles """

    def t_ID(self, t):
        r"(?!\d)[\w]+"
        if self._indented == 1:
            instruction_list, conditional_instruction_list = self.get_instructions_list()
            if t.value.upper() in instruction_list:
                t.type = 'INSTRUCTION'
                t.value = t.value.upper()
            elif t.value.upper() in conditional_instruction_list:
                t.type = 'CONDITIONAL_INSTRUCTION'
                t.value = t.value.upper()
            elif t.value.upper() in self.ASM_REGISTERS:
                t.type = 'REGISTER'
                t.value = t.value.upper()
        else:
            t.type = 'LABEL'
            t.lexer.skip(1)
        return t

    def t_COMMENT(self, t):
        r";(.*)+"

    def t_SIZE(self, t):
        r"(?:\.)[b|w|l|s|B|W|L|S]"
        if t.value.upper() == '.L':
            t.value = 'LONG'
        elif t.value.upper() == '.W':
            t.value = 'WORD'
        elif t.value.upper() == '.B':
            t.value = 'BYTE'
        return t

    def t_REGISTER(self, t):
        r"((A|a|D|d)\d|(PC|pc)|(SR|sr)|(CCR|ccr))"
        t.value = t.value.upper()
        return t

    def t_STRING(self, t):
        r"((?:[\"])(.*?)(?:[\"])|(?:[\'])(.*?)(?:[\']))"
        t.value = t.value[1:-1]
        return t

    def t_BINARY(self, t):
        r"(?:\%)[0-1]+"
        t.value = int(t.value[1:], 2)
        return t

    def t_OCTAL(self, t):
        r"(?:\@)[0-7]+"
        t.value = int(t.value[1:], 8)
        return t

    def t_HEXADECIMAL(self, t):
        r"(?:\$)([0-9A-Fa-f]+)"
        t.value = int(t.value[1:], 16)
        return t

    def t_HEXADECIMAL_0(self, t):
        r"(?:0x)([0-9A-Fa-f]+)"
        t.type = 'HEXADECIMAL'
        t.value = int(t.value[2:], 16)
        return t

    def t_DECIMAL(self, t):
        r"[0-9]+"
        t.value = int(t.value, 10)
        return t

    def t_INDENT(self, t):
        r"[\t|\ ]"
        self._indented = True

    def t_DOT(self, t):
        r'\.'

    def t_COMMA(self, t):
        r'\,'

    def t_HASH(self, t):
        r'\#'
        return t

    def t_DOLLAR(self, t):
        r'\$'
        return t

    def t_LPAR(self, t):
        r'\('
        t.lexer.par = True
        return t

    def t_RPAR(self, t):
        r'\)'
        t.lexer.par = False
        return t

    def t_PLUS(self, t):
        r'\+'
        return t

    def t_MINUS(self, t):
        r'\-'
        return t

    def t_DIV(self, t):
        r'\/'
        return t

    def t_MULT(self, t):
        r'\*'
        return t

    def t_newline(self, t):
        r"[\n|\r\n]+"
        t.lexer.lineno += len(t.value)
        self._indented = False
        self._lines.append(self._line)
        self._line = []

    def t_error(self, t):
        self._errors.append([t, t.lexpos])
        print('Illegal Token:' + t.value[0])
        t.lexer.skip(1)

    # Test it output
    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)


class AssemblerParser(object):
    start = 'main'

    def __init__(self, data):
        # Set up a logging object
        logging.basicConfig(
            level=logging.DEBUG,
            filename="parselog.txt",
            filemode="w",
            format="%(filename)10s:%(lineno)4d:%(message)s"
        )
        log = logging.getLogger()
        self.lexer = AssemblerLexer()
        self.tokens = AssemblerLexer.tokens
        self.parser = yacc.yacc(module=self, debug=True, debuglog=log)
        self.parser.parse(data)

    def p_main(self, p):
        """main : empty
                | label
                | main label"""
        # print('main-input', len(p), p[0:])
        if len(p) == 2:
            p[0] = {'main': [p[1]]}
        if len(p) == 3:
            p[1]['main'].append(p[2])
            p[0] = p[1]
        print('main-output', p[1:])

    def p_label(self, p):
        """label : label statement
                 | LABEL"""
        # print('label-input', len(p), p[0:])
        if hasattr(self, 'instruction'):
            print(self.instruction)
        if len(p) == 2:
            p[0] = {p[1]: []}
        if len(p) == 3:
            items = list(p[1])
            last_item = items[-1]
            p[1][last_item].append(p[2])
            p[0] = p[1]
        # print('label-output', p[0])

    def p_statement(self, p):
        """statement : instruction operation
                     | instruction datasize operation"""
        # print('statement-input', len(p), p[0:])
        if len(p) == 3:
            p[0] = Instruction(p[1], params=p[2])
        if len(p) == 4:
            p[0] = Instruction(p[1], p[2], p[3])
        # print('statement-output', p[1:])

    def p_operation(self, p):
        """operation : addressing_mode
                     | addressing_mode addressing_mode"""
        # print('operation-input', p[1:])
        if len(p) == 3:
            p[0] = [p[1], p[2]]
        else:
            p[0] = [p[1]]
        # print('operation-output', p[1:])

    def p_addressing_mode(self, p):
        """addressing_mode : addressing_mode_none
                           | addressing_mode_direct
                           | addressing_mode_indirect
                           | addressing_mode_indirectpost
                           | addressing_mode_indirectpre
                           | addressing_mode_indirectdisplacement
                           | addressing_mode_indirectindex
                           | addressing_mode_absoluteshort
                           | addressing_mode_absolutelong
                           | addressing_mode_immediate
                           | addressing_mode_range"""
        # print(p[0])
        p[0] = p[1]

    def p_addressing_mode_none(self, p):
        """addressing_mode_none : empty"""
        p[0] = {
            'operation': None,
            'value': '',
        }

    def p_addressing_mode_direct(self, p):
        """addressing_mode_direct : register"""
        if (p[1].type == 'Dn'):
            p[0] = AddrMode_DnDirect([p[1]])
        else:
            p[0] = AddrMode_AnDirect([p[1]])

    def p_addressing_mode_indirect(self, p):
        """addressing_mode_indirect : LPAR register RPAR
                                    | LPAR absolute RPAR"""
        p[0] = AddrMode_AnIndirect([p[1]])

    def p_addressing_mode_indirectpost(self, p):
        """addressing_mode_indirectpost : LPAR register RPAR PLUS"""
        p[0] = AddrMode_AnIndirectPost([p[2]])

    def p_addressing_mode_indirectpre(self, p):
        """addressing_mode_indirectpre : MINUS LPAR register RPAR"""
        p[0] = AddrMode_AnIndirectPre([p[3]])

    def p_addressing_mode_indirectdisplacement(self, p):
        """addressing_mode_indirectdisplacement : absolute LPAR register RPAR"""

        p[0] = AddrMode_AnIndirectDisplacement([p[1], p[3]])

    def p_addressing_mode_indirectindex(self, p):
        """addressing_mode_indirectindex : absolute LPAR register register RPAR"""
        p[0] = AddrMode_AnIndirectIndex([p[1], p[3], p[4]])

    def p_addressing_mode_absoluteshort(self, p):
        """addressing_mode_absoluteshort : absolute SIZE"""
        p[0] = AddrMode_AbsShort([p[1], p[2]])

    def p_addressing_mode_absolutelong(self, p):
        """addressing_mode_absolutelong : absolute"""
        p[0] = AddrMode_AbsLong([p[1]])

    def p_addressing_mode_immediate(self, p):
        """addressing_mode_immediate : immediate"""
        p[0] = AddrMode_Imm([p[1]])

    def p_addressing_mode_range(self, p):
        """addressing_mode_range : register MINUS register DIV register
                                 | register MINUS register DIV register MINUS register"""
        p[0] = {
            'operation': 'range',
            'value': p[1],
        }

    def p_instruction(self, p):
        """instruction : INSTRUCTION
                       | CONDITIONAL_INSTRUCTION"""
        p[0] = p[1]

    def p_datasize(self, p):
        """datasize : SIZE"""
        p[0] = p[1]

    def p_register(self, p):
        """register : REGISTER"""
        p[0] = Register(p[1])

    def p_immediate(self, p):
        """immediate : HASH ID
                     | HASH STRING
                     | HASH BINARY
                     | HASH DECIMAL
                     | HASH OCTAL
                     | HASH HEXADECIMAL"""
        p[0] = p[2]

    def p_absolute(self, p):
        """absolute : ID
                    | BINARY
                    | DECIMAL
                    | OCTAL
                    | HEXADECIMAL"""

    def p_empty(self, p):
        """empty : """
        pass

    def p_error(self, p):
        if p == None:
            return
        else:
            raise SyntaxError(p)


if __name__ == '__main__':
    """ Program Command Line """
    cmd = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            [PYSEGA] 68KASM - SEGA GENESIS 68000 ASSEMBLER
            ----------------------------------------------
            An Sega Genesis 60000 Assembler with focus on
            Development and Romhacking based on Paul McKee
            1986's 68000 Assembler
        ''')
    )
    cmd.add_argument(
        'infile',
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help='Assembler code file.'
    )

    """ Program Main Routine """
    args = cmd.parse_args()

    if(args.infile.name != '<stdin>'):
        with args.infile as asm:
            asmcontent = asm.read()
        AssemblerParser(asmcontent)
    else:
        cmd.print_help()
