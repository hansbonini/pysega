from pysega.base.lexer import Lexer as BaseLexer

class Lexer(BaseLexer):

    ''' Motorola 68000 Conditions Set '''
    ASM_CONDITIONS = [
        'CC', 'CS', 'EQ', 'GE', 'GT', 'HI',
        'LE', 'LS', 'LT', 'MI', 'NE', 'PL',
        'VC', 'VS'
    ]

    ''' Motorola 68000 Opcodes Set '''
    ASM_OPCODES = [
        'ABCD', 'ADD', 'ADDA', 'ADDI', 'ADDQ', 'ADDX',
        'AND', 'ANDI', 'ASL', 'ASR', 'Bcc', 'BCHG',
        'BCLR', 'BRA', 'BSET', 'BSR', 'BTST', 'CHK', 'CLR', 'CMP',
        'CMPA', 'CMPI', 'CMPM', 'DBcc', 'DBF', 'DIVS', 'DIVU',
        'EOR', 'EORI', 'EXG', 'EXT', 'ILLEGAL', 'JMP',
        'JSR', 'LEA', 'LINK', 'LSL', 'LSR', 'MOVE', 'MOVEA',
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

    ''' Motorola 68000 Types Set '''
    ASM_TYPES = [
        'BINARY', 'DECIMAL', 'OCTAL', 'HEXADECIMAL',
        'STRING',
        'OFFSET'
    ]

    """ LEX Tokens """
    tokens = BaseLexer.tokens /
        + ['OPCODE', 'SIZE', 'REGISTER'] /
        + ASM_TYPES

    """ Return Opcodes List """
    def getOpcodes():
        temp = []
        for opcode in ASM_OPCODES:
            if "cc" not in opcode:
                temp.append(opcode)
            else:
                for condition in ASM_CONDITIONS:
                    temp.append(opcode.replace('cc', condition))
        return temp

    """ LEX Tokens Function Rules """
    @lex.TOKEN(r"[0-9A-Za-z_:]+")
    def t_ID(self, t):
        opcodes = getOpcodes()
        if t.value.upper() in opcodes:
            t.type = 'OPCODE'
            t.value = t.value.upper()
        elif t.value.upper() in ASM_REGISTERS:
            t.type = 'REGISTER'
            t.value = t.value.upper()
        return t

    @lex.TOKEN(r"(?:\.)[b|w|l|s|B|W|L|S]")
    def t_SIZE(self, t):
        if t.value.upper() == 'L':
            t.value = 'LONG'
        elif t.value.upper() == 'W':
            t.value = 'WORD'
        else:
            t.value = 'BYTE'
        return t

    @lex.TOKEN(r"((?:[\"])(.*?)(?:[\"])|(?:[\'])(.*?)(?:[\']))")
    def t_STRING(self, t):
        t.value = t.value[1:-1]
        return t

    @lex.TOKEN(r"(?:\#\%)[0-1]+")
    def t_BINARY(self, t):
        t.value = int(t.value[2:],2)
        return t

    @lex.TOKEN(r"(?:\#)[0-9]+")
    def t_DECIMAL(self, t):
        t.value = int(t.value[1:],10)
        return t

    @lex.TOKEN(r"(?:\#\@)[0-7]+")
    def t_OCTAL(self, t):
        t.value = int(t.value[2:],8)
        return t

    @lex.TOKEN(r"(?:\#\$)([0-9A-Fa-f]+)")
    def t_HEXADECIMAL(self, t):
        t.value = int(t.value[2:],16)
        return t

    @lex.TOKEN(r"(?:\$)[0-9A-Fa-f]+")
    def t_OFFSET(self, t):
        t.value = int(t.value[1:],16)
        return t
