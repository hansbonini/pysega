from pprint import pprint
class Parser (object):
    start = 'program'
    def __init__(self, tokens=[]):
      self.tokens = tokens

    def p_program(self, p):
        """program : empty
                    | statement
                    | program statement"""
        if len(p) == 2:
            if p[1] is None:
                p[0] = ('program', [])
            else:
                p[0] = ('program', [ p[1] ])
        elif len(p) == 3:
            if p[1] is None:
                p[0] = p[1]
            else:
                p[0] = ('program', p[1][1] + [ p[2] ])

    def p_empty(self, p):
        """empty : """
        pass

    def p_error(self, p):
        print("Syntax error in input!")
