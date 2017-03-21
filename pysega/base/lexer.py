class Lexer (object):
    tokens = []

    """ LEX Tokens Common Rules """
    t_ignore            = ' ,\t\\'
    t_PLUS              = r'\+'
    t_MINUS             = r'\-'
    t_DIVISION          = r'\\'
    t_LPARENTESIS       = r'\('
    t_RPARENTESIS       = r'\)'
    t_LARROW            = r'\<'
    t_RARROW            = r'\>'

    @lex.TOKEN(r'[\n|\r\n]+')
    def t_newline(self, t):
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def __init__(self):
        pass
