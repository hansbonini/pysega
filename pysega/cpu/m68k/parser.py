from pysega.base.parser import Parser as BaseParser
from pysega.cpu.m68k.instructions import Instructions
from pysega.cpu.m68k.registers import Registers
from pprint import pprint

class Parser(BaseParser):

    def p_statement(self, p):
        """statement : operation """
        p[0] = p[1]
    #            | label
    #            | operand
    #            | comment"""

    #def p_label(self,p):
    #    """label: label"""

    def p_operation(self, p):
        """operation : instruction
                    | instruction addressing_mode
                    | instruction extent
                    | instruction extent addressing_mode"""
        temp = []
        for e in range(1,len(p)):
            temp.append(p[e])
        p[0] = temp


    def p_instruction(self, p):
        """instruction : INSTRUCTION """
        p[0] = getattr(Instructions, p[1].lower())

    def p_extent(self, p):
        """extent : SIZE"""
        p[0] = p[1]

    def p_addressing_mode(self, p):
        """addressing_mode : direct_address
                            | memory_address"""
    # Future implementation
    #                        | special_address
    #                        | implicit_pc """
        p[0] = p[1]

    def p_direct_address_single(self,p):
        """direct_address : register"""
        p[0] = p[1]

    def p_direct_address_complex(self,p):
        """direct_address : register register"""
        p[0] = p[1:]

    def p_memory_address(self,p):
        """memory_address : memory_address_simpleindirect
                            | memory_address_predecrement
                            | memory_address_postincrement
                            | memory_address_displacementindirect
                            | memory_address_indexindirect"""

    def p_memory_address_simpleindirect(self, p):
        """memory_address_simpleindirect : LPARENTESIS REGISTER RPARENTESIS"""

    def p_memory_address_predecrement(self,p):
        """memory_address_predecrement : MINUS LPARENTESIS REGISTER RPARENTESIS"""

    def p_memory_address_postincrement(self, p):
        """memory_address_postincrement : LPARENTESIS OFFSET REGISTER PLUS"""

    def p_memory_address_displacementindirect(self, p):
        """memory_address_displacementindirect : OFFSET LPARENTESIS REGISTER RPARENTESIS"""
        # Falta os Complexos

    def p_memory_address_indexindirect(self, p):
        """memory_address_indexindirect : OFFSET LPARENTESIS REGISTER OFFSET RPARENTESIS"""
        # Falta os Complexos

    def p_register(self, p):
        """register : REGISTER"""
        register = getattr(Registers, p[1][0].lower())
        p[0] = register(register,p[1][1])

    #def p_operand(self, p):
    #    """operand: operand"""

    #def p_comment(self, p):
    #    """comment: comment"""
